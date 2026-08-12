"""Minimal QR encoder (byte mode, ECC level M, versions 1-10). Stdlib only.

Enough for a URL on a business card. Raises ValueError above ~213 bytes rather
than silently truncating.
"""

# (ec_codewords_per_block, blocks_g1, data_cw_g1, blocks_g2, data_cw_g2) at ECC M
_ECC_M = {
    1: (10, 1, 16, 0, 0),
    2: (16, 1, 28, 0, 0),
    3: (26, 1, 44, 0, 0),
    4: (18, 2, 32, 0, 0),
    5: (24, 2, 43, 0, 0),
    6: (16, 4, 27, 0, 0),
    7: (18, 4, 31, 0, 0),
    8: (22, 2, 38, 2, 39),
    9: (22, 3, 36, 2, 37),
    10: (26, 4, 43, 1, 44),
}

_ALIGN = {
    1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30],
    6: [6, 34], 7: [6, 22, 38], 8: [6, 24, 42], 9: [6, 26, 46], 10: [6, 28, 50],
}

# --- GF(256) -----------------------------------------------------------------

_EXP = [0] * 512
_LOG = [0] * 256
_x = 1
for _i in range(255):
    _EXP[_i] = _x
    _LOG[_x] = _i
    _x <<= 1
    if _x & 0x100:
        _x ^= 0x11D
for _i in range(255, 512):
    _EXP[_i] = _EXP[_i - 255]


def _mul(a, b):
    if a == 0 or b == 0:
        return 0
    return _EXP[_LOG[a] + _LOG[b]]


def _gen_poly(n):
    poly = [1]
    for i in range(n):
        nxt = [0] * (len(poly) + 1)
        for j, c in enumerate(poly):
            nxt[j] ^= _mul(c, 1)
            nxt[j + 1] ^= _mul(c, _EXP[i])
        poly = nxt
    return poly


def _ec_codewords(data, n):
    gen = _gen_poly(n)
    rem = list(data) + [0] * n
    for i in range(len(data)):
        coef = rem[i]
        if coef:
            for j, g in enumerate(gen):
                rem[i + j] ^= _mul(g, coef)
    return rem[len(data):]


# --- bit stream --------------------------------------------------------------

def _capacity(version):
    ec, b1, d1, b2, d2 = _ECC_M[version]
    total = b1 * d1 + b2 * d2
    count_bits = 8 if version < 10 else 16
    return total - (4 + count_bits + 7) // 8, total


def _pick_version(nbytes):
    for v in range(1, 11):
        cap, _ = _capacity(v)
        if nbytes <= cap:
            return v
    raise ValueError(
        f"{nbytes} bytes is too much for a version-10 QR (max 213). "
        "Use a shorter URL."
    )


def _bitstream(data, version):
    _, total_data = _capacity(version)
    count_bits = 8 if version < 10 else 16
    bits = []

    def put(value, n):
        for i in range(n - 1, -1, -1):
            bits.append((value >> i) & 1)

    put(0b0100, 4)
    put(len(data), count_bits)
    for byte in data:
        put(byte, 8)

    cap_bits = total_data * 8
    put(0, min(4, cap_bits - len(bits)))
    while len(bits) % 8:
        bits.append(0)

    codewords = [int("".join(str(b) for b in bits[i:i + 8]), 2)
                 for i in range(0, len(bits), 8)]
    pad = [0xEC, 0x11]
    i = 0
    while len(codewords) < total_data:
        codewords.append(pad[i % 2])
        i += 1
    return codewords


def _interleave(codewords, version):
    ec_n, b1, d1, b2, d2 = _ECC_M[version]
    blocks, ecs, pos = [], [], 0
    for _ in range(b1):
        blocks.append(codewords[pos:pos + d1])
        pos += d1
    for _ in range(b2):
        blocks.append(codewords[pos:pos + d2])
        pos += d2
    for block in blocks:
        ecs.append(_ec_codewords(block, ec_n))

    out = []
    for i in range(max(len(b) for b in blocks)):
        for block in blocks:
            if i < len(block):
                out.append(block[i])
    for i in range(ec_n):
        for ec in ecs:
            out.append(ec[i])
    return out


# --- matrix ------------------------------------------------------------------

def _new_matrix(size):
    return [[None] * size for _ in range(size)]


def _place_finder(m, r, c):
    size = len(m)
    for dr in range(-1, 8):
        for dc in range(-1, 8):
            rr, cc = r + dr, c + dc
            if not (0 <= rr < size and 0 <= cc < size):
                continue
            if dr in (-1, 7) or dc in (-1, 7):
                m[rr][cc] = 0
            elif dr in (0, 6) or dc in (0, 6) or (2 <= dr <= 4 and 2 <= dc <= 4):
                m[rr][cc] = 1
            else:
                m[rr][cc] = 0


def _place_alignment(m, version):
    centers = _ALIGN[version]
    size = len(m)
    for r in centers:
        for c in centers:
            if (r < 8 and c < 8) or (r < 8 and c > size - 9) or (r > size - 9 and c < 8):
                continue
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    m[r + dr][c + dc] = 1 if max(abs(dr), abs(dc)) != 1 else 0


def _reserve_format(m):
    size = len(m)
    for i in range(9):
        if m[8][i] is None:
            m[8][i] = 0
        if m[i][8] is None:
            m[i][8] = 0
    for i in range(8):
        if m[8][size - 1 - i] is None:
            m[8][size - 1 - i] = 0
        if m[size - 1 - i][8] is None:
            m[size - 1 - i][8] = 0


def _bch(value, gen, gen_bits):
    v = value << gen_bits
    top = gen.bit_length() - 1
    while v.bit_length() - 1 >= top:
        v ^= gen << (v.bit_length() - 1 - top)
    return v


def _format_bits(mask):
    data = (0b00 << 3) | mask  # 00 = ECC level M
    return ((data << 10) | _bch(data, 0x537, 10)) ^ 0x5412


def _version_bits(version):
    return (version << 12) | _bch(version, 0x1F25, 12)


def _skeleton(version):
    size = version * 4 + 17
    m = _new_matrix(size)
    _place_finder(m, 0, 0)
    _place_finder(m, 0, size - 7)
    _place_finder(m, size - 7, 0)
    _place_alignment(m, version)
    for i in range(8, size - 8):
        bit = 1 if i % 2 == 0 else 0
        if m[6][i] is None:
            m[6][i] = bit
        if m[i][6] is None:
            m[i][6] = bit
    m[size - 8][8] = 1  # dark module
    if version >= 7:
        vb = _version_bits(version)
        for i in range(18):
            bit = (vb >> i) & 1
            m[i // 3][size - 11 + i % 3] = bit
            m[size - 11 + i % 3][i // 3] = bit
    return m


def _free_positions(m):
    """Zigzag scan order over modules still free for data."""
    size = len(m)
    reserved = _new_matrix(size)
    for r in range(size):
        for c in range(size):
            reserved[r][c] = m[r][c] is not None
    _reserve_format(m)
    for r in range(size):
        for c in range(size):
            if m[r][c] is not None:
                reserved[r][c] = True

    out = []
    col = size - 1
    upward = True
    while col > 0:
        if col == 6:
            col -= 1
        rows = range(size - 1, -1, -1) if upward else range(size)
        for row in rows:
            for c in (col, col - 1):
                if not reserved[row][c]:
                    out.append((row, c))
        col -= 2
        upward = not upward
    return out


_MASKS = [
    lambda r, c: (r + c) % 2 == 0,
    lambda r, c: r % 2 == 0,
    lambda r, c: c % 3 == 0,
    lambda r, c: (r + c) % 3 == 0,
    lambda r, c: (r // 2 + c // 3) % 2 == 0,
    lambda r, c: (r * c) % 2 + (r * c) % 3 == 0,
    lambda r, c: ((r * c) % 2 + (r * c) % 3) % 2 == 0,
    lambda r, c: ((r + c) % 2 + (r * c) % 3) % 2 == 0,
]


def _penalty(m):
    size = len(m)
    score = 0
    for line in list(m) + [list(col) for col in zip(*m)]:
        run, prev = 1, line[0]
        for cell in line[1:]:
            if cell == prev:
                run += 1
            else:
                if run >= 5:
                    score += 3 + (run - 5)
                run, prev = 1, cell
        if run >= 5:
            score += 3 + (run - 5)
    for r in range(size - 1):
        for c in range(size - 1):
            block = (m[r][c], m[r][c + 1], m[r + 1][c], m[r + 1][c + 1])
            if all(block) or not any(block):
                score += 3
    pat_a = [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0]
    pat_b = list(reversed(pat_a))
    for line in list(m) + [list(col) for col in zip(*m)]:
        for i in range(size - 10):
            window = line[i:i + 11]
            if window == pat_a or window == pat_b:
                score += 40
    dark = sum(sum(row) for row in m)
    ratio = dark * 100 // (size * size)
    score += 10 * (abs(ratio - 50) // 5)
    return score


def matrix(text):
    """Return the QR module matrix (list of rows of 0/1) for `text`."""
    data = text.encode("utf-8")
    version = _pick_version(len(data))
    codewords = _interleave(_bitstream(data, version), version)

    bits = []
    for cw in codewords:
        for i in range(7, -1, -1):
            bits.append((cw >> i) & 1)

    base = _skeleton(version)
    positions = _free_positions(base)
    bits.extend([0] * (len(positions) - len(bits)))

    best, best_score = None, None
    for mask_id, mask in enumerate(_MASKS):
        m = [row[:] for row in base]
        for (r, c), bit in zip(positions, bits):
            m[r][c] = bit ^ (1 if mask(r, c) else 0)
        _apply_format(m, mask_id)
        score = _penalty(m)
        if best_score is None or score < best_score:
            best, best_score = m, score
    return best


def _format_positions(size):
    """Module coordinates for format bits 14 (first) down to 0 (last), both copies."""
    copy1 = ([(8, c) for c in range(6)] + [(8, 7), (8, 8), (7, 8)]
             + [(r, 8) for r in range(5, -1, -1)])
    copy2 = ([(size - 1 - i, 8) for i in range(7)]
             + [(8, size - 8 + j) for j in range(8)])
    return copy1, copy2


def _apply_format(m, mask_id):
    size = len(m)
    fb = _format_bits(mask_id)
    bits = [(fb >> i) & 1 for i in range(14, -1, -1)]
    for copy in _format_positions(size):
        for (r, c), bit in zip(copy, bits):
            m[r][c] = bit
    m[size - 8][8] = 1


def svg(text, dark="#000000", light=None, quiet=4, module=4):
    """Render `text` as an SVG string. `light=None` leaves the background clear."""
    m = matrix(text)
    size = len(m)
    total = (size + quiet * 2) * module
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="{total}" '
        f'viewBox="0 0 {total} {total}" shape-rendering="crispEdges" role="img" '
        f'aria-label="QR code">'
    ]
    if light:
        parts.append(f'<rect width="{total}" height="{total}" fill="{light}"/>')
    path = []
    for r, row in enumerate(m):
        c = 0
        while c < size:
            if row[c]:
                run = 1
                while c + run < size and row[c + run]:
                    run += 1
                x = (c + quiet) * module
                y = (r + quiet) * module
                path.append(f"M{x} {y}h{run * module}v{module}h-{run * module}z")
                c += run
            else:
                c += 1
    parts.append(f'<path fill="{dark}" d="{"".join(path)}"/></svg>')
    return "".join(parts)


if __name__ == "__main__":
    import sys
    print(svg(sys.argv[1] if len(sys.argv) > 1 else "https://example.com"))
