def get_buildable_roads(edges):
    vertices = get_vertices_from_edges(edges)
    buildable_roads = list(set([
        edge
        for vertex in vertices
        for edge in vertex.edges]))
    return buildable_roads

def get_vertices_from_edges(edges):
    vertices = list(set([
        vertex
        for edge in self.edges
        for vertex in edge.vertices]))
    return vertices

