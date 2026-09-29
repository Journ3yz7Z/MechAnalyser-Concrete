"""Compare the first nine columns and explicitly selected extra channels."""
def norm(value):
    return '' if value is None else str(value).strip()


def cell(row, column):
    return norm(row[column]) if column < len(row) else ''


def units_row(rows, columns):
    row = rows[1] if len(rows) > 1 else ()
    values = [cell(row,c) for c in columns if cell(row,c)]
    if not values:
        return ()
    for value in values:
        if value.startswith('='):
            return ()
        try:
            float(value)
            return ()  # A data row is not a separate unit row.
        except ValueError:
            pass
    return row


def compare_layout(reference, candidate, selected, sheet):
    columns = sorted(set(range(9)) | set(selected))
    rh, ch = reference[0], candidate[0]
    ru, cu = units_row(reference, columns), units_row(candidate, columns)
    for row1,row2,label in ((rh,ch,'列名'),(ru,cu,'单位')):
        for c in columns:
            before,after = cell(row1,c),cell(row2,c)
            if before != after:
                raise ValueError(f'{sheet} 第{c+1}列{label}不同：模板“{before or "空白"}”，该sheet“{after or "空白"}”。请核对列顺序、列名和单位。')
    # Ignore unused extra-column differences, but report once to the user.
    return any(cell(rh,c)!=cell(ch,c) for c in range(9,max(len(rh),len(ch))) if c not in columns)
