from math import pi,cos,sin,atan,sqrt

def rad_to_deg(angle):
    return -angle*180/pi

# def arg(z):
#     x,y=z

    

#     hyp = sqrt(x**2+y**2)
#     # x,y = x/hyp, y/hyp # on ramène les points sur le cercle trigo en gardant le même angle

#     # if x<0 :
#     #     return (rad_to_deg(atan(y/x))+180)%360

#     # return rad_to_deg(atan(y/x))%360


#     return rad_to_deg(2*atan(y/x+hyp))%360

def arg(z)->float:
    """
    arg(z)
    param z: coordonnées (x,y)
    return : argument du (angle entre l'axe des abcisses et le) point z en degré
    """
    x,y=z

    if x==0 :
        if y==0 :
            return 0.0
        if y>0 :
            return 90.0
        return 270.0
    
    hyp = sqrt(x**2+y**2)
    x,y = x/hyp, y/hyp # on ramène les points sur le cercle trigo en gardant le même angle

    if x<0 :
        return round((rad_to_deg(atan(y/x))+180)%360,1)

    return round(rad_to_deg(atan(y/x))%360,1)

# print(arg((-3,-2)))


nb_tests = 50
for i in range(nb_tests):
    angle = (2*pi/nb_tests)*i
    # print(f"x:{cos(angle)}, y:{sin(angle)}")
    print(arg((cos(angle),sin(angle))))



