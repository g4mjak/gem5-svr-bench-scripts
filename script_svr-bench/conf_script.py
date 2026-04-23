from pathlib import Path
import pandas as pd
import altair as alt
import subprocess


config_file = "../gem5-configs/se-neoverse_v2.py"
stats_file = "../output/stats.txt"
ubench= "../../build/ARM/gem5.opt --outdir ../output  ../gem5-configs/se-neoverse_v2.py ../build-arm64/ubench -c ../configs/value_stride.yaml -r 1 -m"
STATS = {
    "ipc": "board.processor.cores.core.ipc",
    "coverage": "board.processor.cores.core.valuePred.predCoverage",
    "accuracy": "board.processor.cores.core.valuePred.accuracy"    
}

results = []

def update_conf(file_path, new_value):
    lines = Path(file_path).read_text().splitlines()
    updated = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"cpu.valuePred.confidence_threshold"):
            lines[i] = f"cpu.valuePred.confidence_threshold = {new_value}"
            updated = True
            break
    if not updated:
        raise ValueError(f"Key 'cpu.valuePred.confidence_threshold' not found in {file_path}")
    Path(file_path).write_text("\n".join(lines) + "\n")


def run_program(command):
    result = subprocess.run(
        command,
        shell=True,          
        check=True,
        capture_output=True,
        text=True
    )
    return result.stdout

def read_stats(file_path,stats):
    result = {}
    n=1
    counters = {name: 0 for name in stats}
    with open(file_path, "r") as f:
        for line in f:
            for name in stats:
                if stats[name] in line:
                    counters[name] += 1
                if counters[name] == n:
                    result[name] = float(line.split()[1])
                    counters[name] = n+1
    
    missing=set(stats)-set(result)
    print(result)
    if missing:
        raise ValueError(f"{missing} not found")
    return result


def plot():
    df=pd.read_csv("results.csv")
    df_long = df.melt(
        id_vars="confidence",
        value_vars=["ipc","coverage","accuracy"],
        var_name="Stat",
        value_name="value"
    )
    print(df)
    print(df_long)
    print(df_long.head())
    print(df_long.dtypes)
    chart= (
        alt.Chart(df_long)
        .mark_line(point=True)
        .encode(
            x=alt.X("confidence:Q", title="Confidence"),
            y=alt.Y("value:Q", title="Values"),
            color="Stat:N",
            tooltip=["confidence:N", "Stat:N","value:Q"]
        )
    ).properties(
        width=1200,
        height=600,
        title="Stats for different confidences of a VP"
    )
    chart.save("plot.html")

def run():
    for confidence in range(2,15):
        print(f"Running with confidence = {confidence}")

        # 1. Modify input
        update_conf(config_file, confidence)

        # 2. Run program
        run_program(ubench)
        # 3. Read output
        metrics = read_stats(stats_file,STATS)

        results.append({
            "confidence": confidence,
            **metrics
        })
    df=pd.DataFrame(results)
    df.to_csv("results.csv",index=False)

def main():
    #print(f"Run")
    run()

    print(f"Plot data")
    plot()

if __name__ =="__main__":
    main()