import json

with open("im_file.json") as f:
    print(f)
    data = json.load(f)
    data["ok"]= "mod"

print(data)

with open("im_file.json", "w") as f:
    json.dump(data, f, indent=4)
