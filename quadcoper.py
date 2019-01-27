import pygame
import matplotlib.pyplot as plt
import random
import math

c_screenWidth = 800
c_screenHeight = 600

# visualization consts
c_meterToPixel = 1000

# Define the colors we will use in RGB format
BLUE = (50, 50, 255)
BLACK = (0, 0, 0)
RED = (255,0,0)
GRAY = (200, 200, 200)

pygame.init()
font = pygame.font.SysFont("Verdana", 12)
screen = pygame.display.set_mode((c_screenWidth, c_screenHeight))
pygame.display.set_caption("Template Simulation")
clock = pygame.time.Clock()


# create a differenced series
def dif(a,b,dt):
    return (a-b)/dt


def MetersToPixels(meters):
    return round(meters * c_meterToPixel)

class Environment:
    def __init__(self):
        self.oslonac = Oslonac()    
        self.sensor = Sensor(self)
        self.reference = Reference()
        self.controller = Controller(self.reference, self.sensor)
        self.sina = Sina(self.controller)
       
    def Update(self, elapsedTime):
        self.sensor.Update(self.sina.ugao,elapsedTime)
        self.controller.Update(self.reference, self.sensor.measurement,self.sina,elapsedTime) #+argument self.sensor.measurement
        self.sina.Update(self.sensor.measurement,elapsedTime) #umesto sensor reada, treba controller.signal

    def Visualize(self):
        self.oslonac.Draw()
        
        self.sina.Draw()

class Sina: 
    def __init__(self,controller):
        self.controller = controller
        self.ugao = 0 * 3.14/180 # u radianima
        self.ugaona_brzina_sine = 0
        self.masa = 10
        self.momentInercije = 1
        self.duzina = 0.5
        self.debljina = 0.02
        self.w = 5
        self.k = 1 # konstanta 
        self.dw = 0
        self.potisak1=8.15
        self.potisak2=0.1

        # define a surface (RECTANGLE)
        self.image = pygame.Surface((MetersToPixels(self.duzina), MetersToPixels(self.debljina)))
        # for making transparent background while rotating an image
        self.image.set_colorkey(BLACK)
        # fill the rectangle / surface with red color
        self.image.fill(RED)
    
    def Update(self,x,dt): # nakon signala kontrolera ovde se racuna trenutnno stanje 
            #update momenta SIle
        ugao_ubrzanje = ((self.potisak1-self.potisak2)*self.duzina/2)/self.momentInercije
        self.ugaona_brzina_sine += ugao_ubrzanje * dt
        print("ugaona brzina ",self.ugaona_brzina_sine)
        self.ugaona_brzina_sine *=0.98
        self.ugao += self.ugaona_brzina_sine*dt 
        #update w+dw
        #update potiska
        self.potisak1 = self.k * (self.w-self.dw) * (self.w-self.dw) 
        self.potisak2 = self.k * (self.w+self.dw) * (self.w+self.dw) 

    def Draw(self):
        new_image = pygame.transform.rotate(self.image, math.degrees(self.ugao))
        rect = new_image.get_rect()
        rect.center = (400, 400)
        screen.blit(new_image, rect)

class Sensor:
    def __init__(self, environment):
        self.environment = environment
        self.measurement = 0.01
        self.bias = 0.0
        self.sigma = 0.004

    def Update(self,ugao,dt):
        noise = random.gauss(self.bias, self.sigma)
        self.measurement = ugao + noise

class Controller:
    def __init__(self, reference, sensor):
        self.reference = reference
        self.sensor = sensor
        self.old = 0
        self.temp = 0 
        #fali logika za control signal

    def Update(self, referenca, measurement,sina,dt):
        # if measurement == referenca.targetValue:
        #     pass

        # if sina.ugao > referenca.targetValue:
        #     sina.dw+=0.1

        # else:
        #     sina.dw-=0.1
        self.old = self.temp
        error_signal = measurement - referenca.targetValue
        self.temp = error_signal
        diff = dif(error_signal,self.old,dt)
        sina.dw = error_signal + diff 

     

class Reference:
    def __init__(self):
        self.targetValue = 30*3.14/180

    def Draw(self, beam):
        pass

class Oslonac:
    def Draw(self):
        pygame.draw.polygon(screen, BLUE, [[400, 400], [430, 500], [370, 500]], 0)

class Logger:
    def __init__(self):
        self.targetValue = []
        self.measuredOutput = []
        self.controlSignal = []
        self.time = []

    def Update(self, env, elapsedTime):
        if (len(self.time) == 0):
            self.time.append(elapsedTime)
        else:
            self.time.append(self.time[-1] + elapsedTime)
        self.targetValue.append(env.reference.targetValue)
        self.controlSignal.append(0)
        self.measuredOutput.append(env.sensor.measurement)

    def Draw(self):
        plt.plot(self.time, self.targetValue)
        plt.plot(self.time, self.measuredOutput, '--')
        plt.xlabel('time [s]')
        plt.legend(['target', 'measurement'])
        plt.show()
        plt.plot(self.time, self.controlSignal)
        plt.xlabel('time [s]')
        plt.ylabel('control signal')
        plt.show()

def Simulation():
    environment = Environment()
    logger = Logger()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # clear the screen every time before drawing new objects  
        screen.fill(GRAY)

        dt = clock.tick(60) / 1000
        environment.Update(dt)
        if running:
            logger.Update(environment, dt)
            environment.Visualize()
            pygame.display.flip()
        else:
            logger.Draw()
            break

if __name__ == '__main__':
    Simulation()