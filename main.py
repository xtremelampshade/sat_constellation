from constellation import fibonacciConstellation

num_satellites = 500
jammed_satellites = [] #[166,852] is an example of satellite list
blocked_satellite_links = [] #[[789,988]] is an example of a satellite link list

c = fibonacciConstellation(
    vertices = num_satellites,
    jammed = jammed_satellites,
    blocked = blocked_satellite_links
)
print(c.dist_between_2_nodes(1,467))