#
# Program for testing FoV for 2D cell-based games, using an optimised
# ray-casting algorithm that only visits each cell once (if at all)
#
# The FoV is always assumed to be a square of odd numbered width, minimum
# 3 cells wide.  The center of the square is the origin of the FoV; all
# rays are drawn from that center to their end point in the FoV.
#
# For the basic algorithm, we exploit the 4-way symmetry of a square.
# In other words, we only need to design a FoV for a wedge like this:
#
#      .
#     ..
#    ...
#   ....
#  .....
# ......

maps = {
    'simple': (
        '         .',
        '        ..',
        '       ...',
        '      ....',
        '     .....',
        '    ......',
        '   .......',
        '  ........',
        ' .........',
        '..........',
    ),

    'short2': (
        '         .',
        '        ..',
        '       ...',
        '      ....',
        '     .....',
        '    ......',
        '   .......',
        '  ........',
        ' #........',
        '.#........',
    ),
    
    'narrow': (
        '         .',
        '        ..',
        '       ...',
        '      ....',
        '     .....',
        '    ......',
        '   .......',
        '  ........',
        ' #########',
        '..........',
    ),

    'angle': (
        '         .',
        '        ..',
        '       ...',
        '      ....',
        '     .....',
        '    ......',
        '   .......',
        '  ........',
        ' #........',
        '..........',
    ),

    'angle2': (
        '         .',
        '        ..',
        '       ...',
        '      ....',
        '     .....',
        '    ......',
        '   .......',
        '  ...#....',
        ' #...#....',
        '..........',
    ),

    'angle3': (
        '         .',
        '        ..',
        '       ...',
        '      ....',
        '     .....',
        '    .#....',
        '   .......',
        '  ...#....',
        ' .........',
        '.....#....',
    ),

    'short1': (
        '         .',
        '        ..',
        '       ...',
        '      ....',
        '     .....',
        '    ......',
        '   .......',
        '  ........',
        ' .........',
        '#.........',
    ),

    'short2': (
        '         .',
        '        ..',
        '       ...',
        '      ....',
        '     .....',
        '    ......',
        '   .......',
        '  ........',
        ' #........',
        '.#........',
    ),
    
    'short3': (
        '         #',
        '        ##',
        '       ###',
        '      .###',
        '     ..###',
        '    ...#..',
        '   .......',
        '  .....#..',
        ' ......###',
        '.......###',
    ),
}

class FOV:
    def __init__(self, size, grid=None):
        self.size = size
        if grid is None:
            self.grid = [ [ '.' ]*(size - t) for t in range(size) ]
        else:
            if len(grid) != size:
                raise ValueError("Grid must be sequence of size "+ size)
            tmp = []
            for y in range(size):
                tmp.append([ t for t in grid[size - y - 1] if t != " " ])
            self.grid = tmp

        # 1 - build all rays (only y values necessary)
        rays = {}
        rayid = 0
        for x in range(1, size, 1):
            for y in range(x+1):
                angle = y / x
                rays[rayid] = tuple(( round(t*angle) for t in range(x+1) ))
                rayid += 1

        # 2 - remove all lines fully contained within another line
        while rayid > 0:
            rayid -= 1
            cray = rays[rayid]
            for ray in ( t for t in rays if len(rays[t]) > len(cray) ):
                if cray == rays[ray][:len(cray)]:
                    #print(cray, "is fully inside", rays[ray])
                    del rays[rayid]
                    break

        # 3 - normalise rayids
        rayid = 0
        normrays = {}
        for ray in sorted(rays.values(), key=lambda x: len(x)):
            normrays[rayid] = ray
            rayid += 1
        self.rays = normrays

        # 4 - create lines number array
        lines = {}
        for rayid, ray in normrays.items():
            #print(rayid, ray)
            for x in range(len(ray)):
                coor = (x, ray[x])
                num = lines.get(coor, 0) | 2**rayid
                lines[coor] = num
                
        self.lines = lines

        # 5 - create mask array
        mask = [ 0 ]*self.size
        for x in range(self.size):
            candidates = { t: normrays[t] for t in normrays if len(normrays[t]) < x+1 }.keys()
            if not candidates:
                continue
            mask[x] = (2**len(normrays) - 1) ^ (2**(max(candidates) + 1) - 1)
        self.mask = mask

    def render_fov(self):
        self.iterations = self.gridlookups = 0
        self.fov = [ [ False ]*(self.size - t) for t in range(self.size) ]
        valid_rays = mask = self.lines[(0, 0)]
        for x in range(self.size):
            if self.mask[x]:
                valid_rays &= self.mask[x]

            for y in range(x+1):
                lines = self.lines[(x, y)]
                self.iterations += 1
                if lines & valid_rays:
                    self.fov[y][x - y] = True
                    self.gridlookups += 1
                    if self.grid[y][x - y] == '.':
                        continue
                    valid_rays &= (mask ^ lines)
                    
            if not valid_rays:
                break
        
            
    def print(self):
        for l in range(self.size):
            y = self.size - l - 1
            print(" "*y + "".join([ self.fov[y][x] and self.grid[y][x] or "?" for x in range(self.size - y) ]))
        print("Iterations:", self.iterations)
        print("Grid look ups:", self.gridlookups)
        #print("Size of graph:", len(self.graph))
        #print("Size of graph visited:", len(self.graph_visited))


if __name__ == '__main__':
    fov = FOV(10, maps['short3'])
    
    fov.render_fov()
    fov.print()
