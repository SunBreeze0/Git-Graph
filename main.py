import os
import subprocess
import argparse
from typing import List, Dict
from graphviz import Digraph

def get_commit_graph(repo_path: str, target_file: str) -> Dict[str, List[str]]:
    os.chdir(repo_path)
    result = subprocess.run(
        ["git", "log", "--pretty=format:%H", "--name-only", "--", target_file],
        capture_output=True, text=True
    )
    log_entries = result.stdout.split("\n")
    graph = {}
    current_commit = None
    for line in log_entries:
        if not line.strip():
            continue
        if len(line) == 40:
            current_commit = line.strip()
            graph[current_commit] = []
        elif current_commit:
            graph[current_commit].append(line.strip())
    return graph

def generate_mermaid_code(graph: Dict[str, List[str]]) -> str:
    mermaid_code = ["graph TD"]
    for commit, files in graph.items():
        for file in files:
            mermaid_code.append(f"    {commit} --> {file}")
    return "\n".join(mermaid_code)

def save_to_file(output_path: str, content: str):
    with open(output_path, "w") as file:
        file.write(content)

def generate_graphviz_pdf(graph: Dict[str, List[str]], output_graph: str):
    name, extension = os.path.splitext(output_graph)
    format = extension.lstrip(".")
    dot = Digraph(format=format)
    dot.attr(rankdir="TB")
    for commit, files in graph.items():
        for file in files:
            dot.edge(commit, file)
    dot.render(name, cleanup=True)
    print(f"Graph saved to {output_graph}")

def main():
    parser = argparse.ArgumentParser(description="Visualize Git commit dependencies.")
    parser.add_argument("--repo-path", required=True, help="Path to the Git repository.")
    parser.add_argument("--target-file", required=True, help="File to analyze dependencies for.")
    parser.add_argument("--output-file", required=True, help="Path to the output file for Mermaid code.")
    parser.add_argument("--output-graph", required=True, help="Path to the output graph file.")
    args = parser.parse_args()
    try:
        graph = get_commit_graph(args.repo_path, args.target_file)
        mermaid_code = generate_mermaid_code(graph)

        save_to_file(args.output_file, mermaid_code)
        generate_graphviz_pdf(graph, args.output_graph)
        print(f"Dependency graph saved to {args.output_file}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()