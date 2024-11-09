# -*- coding: cp1251 -*-

import configparser
import subprocess
import graphviz
import os

class DependencyVisualizer:
    def __init__(self, config_path):
        config = configparser.ConfigParser()
        with open(config_path, 'r', encoding='cp1251') as file:
            config.read_file(file)        
        self.config = config
        self.repo_path = self.config["Repository"]["path"]
        self.tag_name = self.config["Repository"]["tag"]
        self.graphviz_program_path = self.config["Graphviz"]["program_path"]
        self.graph_save_path = "C:/Users/vpetr/source/repos/Config_Task_2/Config_Task_2/graphs"
        
    def load_config(self, config_path):
        config = configparser.ConfigParser()
        with open(config_path, 'r', encoding='cp1251') as file:
            config.read_file(file)
        return config
    
    def get_commit_dependencies(self):
        """Fetch all commit dependencies in the repository."""
        commits = subprocess.check_output(
            ["git", "-C", self.repo_path, "rev-list", "--all", "--parents"],
            text=True
        ).strip().split("\n")
        
        dependencies = {}
        for line in commits:
            parts = line.split()
            commit = parts[0]
            parents = parts[1:]
            dependencies[commit] = parents
        return dependencies
    
    def visualize_graph(self, dependencies):
        """Build and render graph using Graphviz with a specified path to the Graphviz executable."""
        graph = graphviz.Digraph(format='png')
        graph.attr(rankdir='LR')
        
        for commit, parents in dependencies.items():
            graph.node(commit, label=commit[:7])  
            for parent in parents:
                graph.edge(parent, commit)
        
        graph_path = os.path.join(self.graph_save_path, "dependency_graph")

        graph.render(graph_path, engine='dot', directory=self.graphviz_program_path)
        return f"{graph_path}.png"

    def run(self):
        dependencies = self.get_commit_dependencies()
        output_path = self.visualize_graph(dependencies)
        print(f"Graph created at {output_path}")


if __name__ == "__main__":
    visualizer = DependencyVisualizer("C:/Users/vpetr/source/repos/Config_Task_2/Config_Task_2/config.ini")
    visualizer.run()
 #py Config_Task_2\Config_Task_2.py