"""User-selected initial specimen conditions; never overwrite filled metadata."""
DEFAULT_METADATA = dict(test_type='单轴压缩试验', material='水泥砂浆',
                        cement_ratio='1', aggregate_ratio='2', water_content='13',
                        pressure='0', injection_hours='24', curing_days='28')


def fill_defaults(metadata):
    changed = False
    for key, value in DEFAULT_METADATA.items():
        if metadata.get(key) is None or not str(metadata.get(key, '')).strip():
            metadata[key] = value
            changed = True
    return changed
