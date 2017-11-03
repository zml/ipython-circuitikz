"""
An IPython extension for generating circuit diagrams using LaTeX/Circuitikz
from within ipython notebook.
"""
import os,sys,subprocess
import re
from IPython.core.magic import magics_class, cell_magic, Magics
from IPython.display import Image, SVG

latex_template = r"""\documentclass{standalone}
\usepackage{tikz}
\usepackage[%s]{circuitikz}
\begin{document}
%s
\end{document}
"""

@magics_class
class Circuitikz(Magics):

    @cell_magic
    def circuitikz(self, line, cell):
        """Generate and display a circuit diagram using LaTeX/Circuitikz.
        
        Usage:
        
            %circuitikz [key1=value1] [key2=value2] ...

            Possible keys and default values are

                filename = ipynb-circuitikz-output
                dpi = 100 (for use with format = png)
                options = europeanresistors,americaninductors
                format = svg (svg or png)

        """
        options = {'filename': 'ipynb-circuitikz-output',
                   'dpi': '100',
                   'format': 'png',
                   'options': 'europeanresistors,americaninductors'}
        
        args = re.sub(r"[\t\s]*=[\t\s]*","=",line).split()
        for option in args:
            try:
                key, value = option.split("=")
                if key in options:
                    options[key] = value
                else:
                    print("Unrecongized option %s" % key)
            except:
                pass

        filename = options['filename']
        code = cell

        for ext in ["tex", "pdf", "png"]:
            try:
                os.remove("%s.%s" % (filename, ext))
            except:
                pass

        with open(filename + ".tex", "w") as file:
            file.write(latex_template % (options['options'], cell))
        
        try:
            subprocess.call(("pdflatex -interaction batchmode %s.tex" % filename).split())
            for ext in ["aux", "log"]:
                os.remove("%s.%s" % (filename, ext))

            subprocess.call(("pdfcrop %s.pdf %s-tmp.pdf" % (filename, filename)).split())
            os.rename("%s-tmp.pdf" % filename, "%s.pdf" % filename)
    
            if options['format'] == 'png':
                subprocess.call(("convert -density %s %s.pdf %s.png" % (options['dpi'], filename, filename)).split())
                result = Image(filename=filename + ".png")
            else:
                subprocess.call(("pdf2svg %s.pdf %s.svg" % (filename, filename)).split())
                result = SVG(filename + ".svg")
            return result
        except OSError as e:
            print("Execution failed:", e, file=sys.stderr)

def load_ipython_extension(ipython):
    ipython.register_magics(Circuitikz)
