import pandas as pd


def mean_average(data, mean_width):
    new_array = []
    mean_width = int(mean_width)
    half_width = int(mean_width / 2)

    # for _ in range(half_width):
    #     new_array.append(0)

    for idx, _ in enumerate(data):
        if idx < half_width:
            newValue = None
        elif idx > len(data) - (half_width + 1):
            newValue = None
        else:
            newValue = sum(data[idx - half_width : idx + half_width + 1]) / mean_width
        new_array.append(newValue)

    # for _ in range(half_width):
    #     new_array.append(0)

    return new_array


def GetFiltered_clpr(data):
    print(data)
    columns = ["dates", "values"]
    df = pd.DataFrame(columns=columns)

    for row in data["output2"]:
        dateText = f"{row['stck_bsop_date'][2:4]}/{row['stck_bsop_date'][4:6]}/{row['stck_bsop_date'][6:8]}"
        # dateText = f"{row['stck_bsop_date'][4:6]}/{row['stck_bsop_date'][6:8]}"
        new_row = pd.DataFrame([{"dates": dateText, "values": int(row["stck_clpr"])}])
        df = pd.concat([df, new_row], ignore_index=True)

    print(df)
    return df
