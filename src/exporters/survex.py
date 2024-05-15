# pylint: disable=R0903
"""
Survex exporter - exports cave data to a Survex file using Jinja2 templates.
"""

import os
from jinja2 import Environment, FileSystemLoader
from models import CaveData


class SurvexExporter:
    """
    Class to export cave data to a Survex file using Jinja2 templates.
    """

    def __init__(self, template_dir=None):
        if template_dir is None:
            template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def export(self, data: CaveData, output_path: str, cave_name: str):
        """
        Export cave data to a Survex file.
        """
        template = self.env.get_template("survex_template.jinja")
        output = template.render(cave_name=cave_name, cave_data=data)

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(output)
