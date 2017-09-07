class terminal:
    def terminal_query_version(self, id):
        return { 'cmd': 'query', 'query': 'version', 'id': id }

    def terminal_add_terminal(self, id, size, font='9x15'):
        return {
            'cmd': 'add_terminal',
            'data': {
                'font': font,
                'width': size[0],
                'height': size[1],
                'id': id,
            },
        }

    def terminal_add_window(
            self, id, pos, size,
            parent='root', fgcolour=(255, 255, 255, 255), bgcolour=(0, 0, 0, 255),
            cursorVisible=False,
    ):
        return {
            'cmd': 'add_window',
            'data': {
                'width': size[0],
                'height': size[1],
                'id': id,
                'parent': parent,
                'position': { 'x': pos[0], 'y': pos[1] },
                'colour': ( bgcolour, fgcolour ),
                'cursorVisible': cursorVisible,
            },
        }

    def terminal_set_active_window(self, window):
        return {
            'cmd': 'set_active_window',
            'data': {
                'window': window,
            }
        }

    def terminal_push_input(self, terminal, window, mode='line', prompt='> '):
        return {
            'cmd': 'push_input',
            'data': {
                'terminal': terminal,
                'window': window,
                'mode': mode,
                'prompt': prompt,
            }
        }

    
