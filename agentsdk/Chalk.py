class Chalk:
    _red: str = "\033[91m"
    _blue: str = "\033[94m"
    _yellow: str = "\033[93m"
    _purple: str = "\033[95m"
    _cyan: str = "\033[96m"
    _grey: str = "\033[96m"
    _reset: str = "\033[0m"

    def yellow(self, text: str):
        return f"{self._yellow}{text}{self._reset}"

    def purple(self, text: str):
        return f"{self._purple}{text}{self._reset}"

    def blue(self, text: str):
        return f"{self._blue}{text}{self._reset}"

    def red(self, text: str):
        return f"{self._red}{text}{self._reset}"

    def grey(self, text: str):
        return f"{self._grey}{text}{self._reset}"


chalk = Chalk()
