def format_percent(value, digits=2):
    return f"{value * 100:.{digits}f}%"


def format_weights(weights, asset_names, digits=3):
    return {
        asset_names[index]: round(float(weights[index]), digits)
        for index in range(len(asset_names))
    }