with open(r"C:\Users\krsna\Downloads\Python Projects\app.py") as f:
    content = f.read()

start = content.find("features = [")
if start >= 0:
    end_marker = "feature_grid(features, cols=3)"
    end = content.find(end_marker)
    if end >= 0:
        end = content.find("\n", end) + 1
        content = content[:start].rstrip() + "\n\nst.markdown(\"## Core Capabilities\")\nst.markdown(\"Use the sidebar to navigate between Strategy Generator, Backtester, Optimizer, Genetic Evolution, Charts, Strategy Database, and AI Chat.\")\n"
        with open(r"C:\Users\krsna\Downloads\Python Projects\app.py", "w") as f2:
            f2.write(content)
        print("done")
    else:
        print("end not found")
else:
    print("start not found")
