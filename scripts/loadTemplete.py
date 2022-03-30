import json
import random

services = list(range(1,11))

random.shuffle(services)

templete = {
    "designation": None,
    "probability": 50,
    "faults": {
        "before": [{"type": "latency", "args": { "delay": 600 }}],
        "after": [{"type": "latency", "args": { "delay": 600 }}]
    },
    "routes": None
}


def create_route(k, last_designation=None):
    path = None
    
    if k <= 15:
        k+=1
        route = templete.copy()
        route['designation'] = f"service_{services[random.randint(0,len(services)-1)]}"
        while route['designation'] == last_designation:
            route['designation'] = f"service_{services[random.randint(0,len(services)-1)]}"
        route['probability'] = random.randint(50, 100)
        route['faults']['before'][0]['args']['delay'] = random.randint(100, 400)
        route['faults']['after'][0]['args']['delay'] = random.randint(100, 400)
        route['routes'] = [create_route(k,  route['designation'])]
        if route['routes'][0] == None:
            route['routes'] = None
        # for i in range(random.randint(0,2)):
        #     k+=1
        #     sub_route = create_route(k)
        #     if sub_route:
        #         route['routes'].append(sub_route)
        #     else:
        #         route['routes'] = None
        #         break
        
        path = route
   
    return path

out_file = open("routes.json", "w")
  
json.dump(create_route(0), out_file, separators=(',', ':'))