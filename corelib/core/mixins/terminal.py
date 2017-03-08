class terminal:
    def terminal_version(self, version):
        return { 'type': 'version', 'version': version }

    def terminal_add_terminal(self, id, font, size):
        return {
            'type': 'command',
            'command': 'add_terminal',
            'data': {
                'font': font,
                'width': size[0],
                'height': size[1],
                'id': id,
            },
        }
