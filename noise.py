import math

class Noise:
    @staticmethod
    def perlin_noise(x, y):
        total = 0.0
        persistence = 0.5
        octaves = 4
        frequency = 0.1
        amplitude = 1.0

        for i in range(octaves):
            total += Noise.interpolated_noise(x * frequency, y * frequency) * amplitude
            amplitude *= persistence
            frequency *= 2  # Lacunarity

        return total

    @staticmethod
    def noise(x, y):
        n = x + y * 57
        n = (n << 13) ^ n
        return 1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0

    @staticmethod
    def smoothed_noise(x, y):
        corners = (Noise.noise(x - 1, y - 1) + Noise.noise(x + 1, y - 1) +
                   Noise.noise(x - 1, y + 1) + Noise.noise(x + 1, y + 1)) / 16.0
        sides = (Noise.noise(x - 1, y) + Noise.noise(x + 1, y) +
                 Noise.noise(x, y - 1) + Noise.noise(x, y + 1)) / 8.0
        center = Noise.noise(x, y) / 4.0
        return corners + sides + center

    @staticmethod
    def interpolated_noise(x, y):
        integer_X = int(x)
        fractional_X = x - integer_X

        integer_Y = int(y)
        fractional_Y = y - integer_Y

        v1 = Noise.smoothed_noise(integer_X, integer_Y)
        v2 = Noise.smoothed_noise(integer_X + 1, integer_Y)
        v3 = Noise.smoothed_noise(integer_X, integer_Y + 1)
        v4 = Noise.smoothed_noise(integer_X + 1, integer_Y + 1)

        i1 = Noise.interpolate(v1, v2, fractional_X)
        i2 = Noise.interpolate(v3, v4, fractional_X)

        return Noise.interpolate(i1, i2, fractional_Y)

    @staticmethod
    def interpolate(a, b, x):
        ft = x * math.pi
        f = (1 - math.cos(ft)) * 0.5
        return a * (1 - f) + b * f
