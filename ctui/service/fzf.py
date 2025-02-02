from pyfzf.pyfzf import FzfPrompt


class FZF:
    def __init__(self, core):
        self.core = core
        self.fzf = FzfPrompt()

        if self.core.ui.color_scheme == "dark":
            self.options = '--color=hl:red,bg:black,fg:white,fg+:black,bg+:#dddddd,hl+:red,spinner:white,prompt:white,info:grey --pointer="" --marker=""'
        else:
            self.options = '--color=hl:red,fg+:#000000,bg+:#eeeeee,hl+:red,spinner:black,prompt:black,info:grey --pointer="" --marker=""'

    def prompt(self, list):
        return self.fzf.prompt(list, self.options)
