# -*- coding: cp1251 -*-

import configparser
import subprocess
import graphviz
import os

class DependencyVisualizer:
    def __init__(self, config_path):
        # Загружаем конфигурацию
        config = configparser.ConfigParser()
        with open(config_path, 'r', encoding='cp1251') as file:
            config.read_file(file)
        self.config = config

        # Извлекаем пути из конфигурации
        self.repo_path = self.config["Repository"]["path"]
        self.tag_name = self.config["Repository"]["tag"]
        self.graphviz_program_path = self.config["Graphviz"]["program_path"]
        self.graph_save_path = "C:/Users/vpetr/source/repos/Config_Task_2/Config_Task_2/graphs"

    def get_commit_dependencies(self):
        
        
        # Получаем хеш коммита, связанного с тегом
        tag_commit = subprocess.check_output(
            ["git", "-C", self.repo_path, "rev-list", "-n", "1", self.tag_name],
            text=True
        ).strip()
        
        # Получаем коммиты и их зависимости, начиная с указанного тега
        commits = subprocess.check_output(
            ["git", "-C", self.repo_path, "rev-list", "--parents", tag_commit],
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
    
        
        # Временно добавляем путь к Graphviz в переменную окружения PATH
        original_path = os.environ["PATH"]
        os.environ["PATH"] += os.pathsep + self.graphviz_program_path
        
        try:
            graph = graphviz.Digraph(format='png')
            graph.attr(rankdir='LR')
            
            for commit, parents in dependencies.items():
                graph.node(commit, label=commit[:7])  
                for parent in parents:
                    graph.edge(parent, commit)
            
            graph_path = os.path.join(self.graph_save_path, "dependency_graph")

            graph.render(graph_path, engine='dot')
            return self.graph_save_path
        
        finally:
            # Восстанавливаем оригинальный PATH
            os.environ["PATH"] = original_path

    def run(self):
        dependencies = self.get_commit_dependencies()
        output_path = self.visualize_graph(dependencies)
        print(f"Graph created at {output_path}")


if __name__ == "__main__":
    visualizer = DependencyVisualizer("C:/Users/vpetr/source/repos/Config_Task_2/Config_Task_2/config.ini")
    visualizer.run()
