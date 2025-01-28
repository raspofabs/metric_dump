import json

def run():
    with open("data_dump.log") as fh:
        lines = fh.read()
    output = []
    for line in lines.split("\n"):
        try:
            if line:
                output.append(json.loads(line))
        except:
            print(f"LINE: {line}")
            raise
    with open("profile_dump.json", "w") as fh:
        fh.write(json.dumps(output, indent=" "))
