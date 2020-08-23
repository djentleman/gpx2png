from PIL import Image, ImageDraw
import gpxpy
import gpxpy.gpx
import argparse

imgsize = 800
padding = 10


def get_args(arg_list=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('gpx_file')
    args = parser.parse_args(arg_list)
    return args

def get_normalized_route(track):
    # scale everything between 0 and 1000
    # need to use a consistent scaling ratio or the map will look squashed
    points = []
    for segment in track.segments:
        for point in segment.points:
            points.append((point.latitude, point.longitude))

    # find the x diff and the y diff
    # the bigger diff will become the scaler
    X = [p[0] for p in points]
    Y = [p[1] for p in points]
    delta_x = max(X) - min(X)
    delta_y = max(Y) - min(Y)
    if delta_x >= delta_y:
        scaling_factor = (imgsize - padding*2) / delta_x
    else:
        scaling_factor = (imgsize - padding*2) / delta_y
    
    # we also need to translate everything to start at 0, 0 lets use min_x, min_y as 0, 0
    translate_factor_x =  -min(X)
    translate_factor_y =  -min(Y)

    # now lets do the the transform
    return [
        (
            padding + ((x + translate_factor_x) * scaling_factor),
            padding + ((y + translate_factor_y) * scaling_factor),
        )
        for x, y in points
    ]


def draw_png(points):
    img = Image.new('RGBA', (imgsize, imgsize), (255, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for i in range(len(points)-1):
        curr = points[i]
        succ = points[i+1]
        draw.line([curr, succ], fill=(255, 255, 255), width=3)
    return img



def convert_track_to_png(track):
    points = get_normalized_route(track)
    png = draw_png(points)
    return png

def main():
    args = get_args()
    gpx = gpxpy.parse(open(args.gpx_file, 'r+'))


    tracks = gpx.tracks
    for track in tracks:
        fname = track.name.lower().replace(' ', '_')
        png = convert_track_to_png(track)
        png.save(f'{fname}.png', 'PNG')

if __name__ == '__main__':
    main()
