import unittest

import sys
sys.path.append('C:/Users/vpetr/source/repos/Config_Task_2/Config_Task_2')
from Config_Task_2 import DependencyVisualizer

from unittest.mock import patch, mock_open, MagicMock
import subprocess
import os


class TestDependencyVisualizer(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data="[Repository]\npath=C:/path/to/repo\ntag=v1.0.0\n[Graphviz]\nprogram_path=C:/Program Files/Graphviz/bin")
    def test_load_config(self, mock_file):
        """Test that the configuration is loaded correctly."""
        visualizer = DependencyVisualizer("fake_path/config.ini")
        
        self.assertEqual(visualizer.repo_path, "C:/path/to/repo")
        self.assertEqual(visualizer.tag_name, "v1.0.0")
        self.assertEqual(visualizer.graphviz_program_path, "C:/Program Files/Graphviz/bin")
        mock_file.assert_called_once_with("fake_path/config.ini", 'r', encoding='cp1251')
    @patch('builtins.open', new_callable=mock_open, read_data="[Repository]\npath=C:/path/to/repo\ntag=v1.0.0\n[Graphviz]\nprogram_path=C:/Program Files/Graphviz/bin")
    @patch('subprocess.check_output')
    def test_get_commit_dependencies(self, mock_subprocess, mock_file):
        """Test that commit dependencies are parsed correctly."""
        mock_subprocess.return_value = (
            "e9682c6 43e40e6\n"
            "43e40e6 d33b40a\n"
            "d33b40a b712b6d\n"
            "b712b6d\n"
        )
        
        visualizer = DependencyVisualizer("fake_path/config.ini")
        dependencies = visualizer.get_commit_dependencies()
        
        expected_dependencies = {
            "e9682c6": ["43e40e6"],
            "43e40e6": ["d33b40a"],
            "d33b40a": ["b712b6d"],
            "b712b6d": []
        }
        
        self.assertEqual(dependencies, expected_dependencies)
        mock_subprocess.assert_called_once_with(
            ["git", "-C", visualizer.repo_path, "rev-list", "--all", "--parents"],
            text=True
        )
    @patch('builtins.open', new_callable=mock_open, read_data="[Repository]\npath=C:/path/to/repo\ntag=v1.0.0\n[Graphviz]\nprogram_path=C:/Program Files/Graphviz/bin")
    @patch('graphviz.Digraph.render')
    def test_visualize_graph(self, mock_render, mock_file):
        """Test that the graph visualization is created correctly."""
        mock_render.return_value = None  # Mock the render method to avoid actual file generation
        
        visualizer = DependencyVisualizer("fake_path/config.ini")
        dependencies = {
            "e9682c6": ["43e40e6"],
            "43e40e6": ["d33b40a"],
            "d33b40a": ["b712b6d"],
            "b712b6d": []
        }
        
        graph_path = visualizer.visualize_graph(dependencies)
        
        expected_path = os.path.join(visualizer.graph_save_path, "dependency_graph.png")
        self.assertEqual(graph_path, expected_path)
        mock_render.assert_called_once_with(
            os.path.join(visualizer.graph_save_path, "dependency_graph"),
            engine='dot',
            directory=visualizer.graphviz_program_path
        )

if __name__ == "__main__":
    unittest.main()