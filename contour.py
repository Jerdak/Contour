'''
	Generate a 2D contour map from any image though the intent
	is to generate the contour map from a heightmap.
 
	Heights are first binned in to groups.  These groups
	are then run through a very simple edge detection alg.
 
	Author: Jeremy Carson
 
	Requirements: 	Python 2.5 (tested on 2.5, might work w/ others)
			Python Imaging Library (version??)
'''
import sys
import argparse

from PIL import Image

def hex_to_rgb(hex):
	rs = hex[0:2]
	bs = hex[2:4]
	gs = hex[4:6]

	r = int(rs,16)
	g = int(bs,16)
	b = int(gs,16)
	return (r,g,b)

# Based on a 9-class sequential color scheme
# from http://colorbrewer2.org/
sequenial_colors = [
	hex_to_rgb("f7fcfd"),
	hex_to_rgb("e0ecf4"),
	hex_to_rgb("bfd3e6"),
	hex_to_rgb("9ebcda"),
	hex_to_rgb("8c96c6"),
	hex_to_rgb("8c6bb1"),
	hex_to_rgb("88419d"),
	hex_to_rgb("810f7c"),
	hex_to_rgb("4d004b"),
]
 

def greyscale(img):
	""" Convert RGB to greyscale
	"""
	width = img.size[0]
	height = img.size[1]
	pixels = img.load()
	for y in range(0,height):
		for x in range(0,width):
			rgb = pixels[x,y]
			g = rgb[0] * 0.3 + rgb[1] * .59 + rgb[2] * .11
			rgb = (int(g),int(g),int(g))
			pixels[x,y] = rgb
	return img 

def bin(img,layerCount):
	""" Bin pixel colors based on a maximum number of layers(layerCount)

		Input:
			layerCount - Number of 'bins' for the input image.  Should not exceed 9
			img - greyscale image
		Note:
			This function assumes the input image is greyscale so it only looks
			at the 'red' channel of each pixel color.  Typical heightmaps encode heights
			as greyscale.
	"""
	if layerCount > 9:
		raise ValueError("layerCount cannot exceed 9") 

	width = img.size[0]
	height = img.size[1]
	pixels = img.load()

	minColor = 999999.0
	maxColor = -minColor
 
	# pull out min/max color 
	for y in range(0,height):
		for x in range (0,width):
			if pixels[x,y][0] > maxColor:
				maxColor = float(pixels[x,y][0])
			if pixels[x,y][0] < minColor:
				minColor = float(pixels[x,y][0])
 	
 	# generate the bin size
	layerStep = (maxColor - minColor) / layerCount 

	# reapply bin color to input image.
	for y in range(0,height):
		for x in range (0,width): 
			layer = int(pixels[x,y][0]/layerStep)
			pixels[x,y] = (layer,layer,layer)
 	return img

def is_edge_pixel(img,pixels,x,y):
	""" Returns true if pixel[x,y] borders a different color than itself.
	"""
	uniqueColors = {}
	for r in range(-1,2):
		for c in range(-1,2):
			if isinrange(x+r,y+c,img.size[0],img.size[1]):
				if pixels[x+r,y+c] != pixels[x,y]:
					return True
	return False

def edge(img):
	"""	Extract edges (regions between bins) and color them on the image

		Input:
			img - binned image.  e.g. edge(bin(grey(img),9))
	"""
	width = img.size[0]
	height = img.size[1]
	pixels = img.load()
	edge_pixels = []
	old_pixels = []
 	
	# First pass through image to find the edges.  Edges rely
	# on pixel differences so we can't modify the pixels in this loop.
 	for y in range(0,height):
		for x in range (0,width): 
			result = is_edge_pixel(img,pixels,x,y)
			if result:
				edge_pixels.append((x,y))
			else:
				old_pixels.append((x,y))

	# Paint old (non-edge) pixels with a sequential color
	for pair in old_pixels:
		old_color = pixels[pair[0],pair[1]] 
		new_color = sequenial_colors[old_color[0]]
		pixels[pair[0],pair[1]] = new_color

	# Paint edges red so they are visible against the sequential color.
	# Red chosen from http://colorbrewer2.org/#
	edge_color = hex_to_rgb("e31a1c")

	for pair in edge_pixels:
		pixels[pair[0],pair[1]] = edge_color
			

#Is x,y coordinate in range of the input image	
def isinrange(x,y,width,height):
	return (x>=0 and x < width and y >=0 and y < height)

def main():
	parser = argparse.ArgumentParser(description="Extract contour regions and edges from an image, typically a heightmap")
	parser.add_argument("input_image", help="input image file")
	parser.add_argument("output_image", help="output image file")
	parser.add_argument("-l","--layercount",help="number of layers(bins).  Should not exceed 9. (Default = 5)",default=5,type=int)
	args = parser.parse_args()


	if args.input_image == args.output_image:
		raise ValueError("input image should not match output image")
	if args.layercount > 9:
		raise ValueError("layer count cannot exceed 9")

	img = Image.open(args.input_image)
	greyscale(img)
	bin(img,args.layercount)
	edge(img)
	img.save(args.output_image)	
if __name__=='__main__':
	main()
