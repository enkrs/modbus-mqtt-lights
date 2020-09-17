Gaismu kontroles MQTT protokola specifikācija
=============================================

Piemēra kontroliera nosaukums ir `lightcontrol` un tam ir pieejami divi mezgli ar gaismām - `warehouse` un `office`

Kontroliera dati:
```
homie/lightcontrol/$homie - "4.0.0"
homie/lightcontrol/$name - "Light control panel"
homie/lightcontrol/$state - "init", "ready", "disconnected", "sleeping", "lost", "alert"
homie/lightcontrol/$nodes - "warehouse[],office[]"
homie/lightcontrol/$extensions - ""
```

Dati par katru gaismu:

````
homie/lightcontrol/lights/1/$name - "Gaisma 1"
homie/lightcontrol/lights/1/$type - "Standarta apgaismojums"
homie/lightcontrol/lights/1/$properties - "power"
homie/lightcontrol/lights/1/power/$name - "Lampa"
homie/lightcontrol/lights/1/power/$datatype - "boolean"
homie/lightcontrol/lights/1/power/$settable - "true"
homie/lightcontrol/lights/1/power/$retained - "true"
````

The device must subscribe to this topic if the property is settable:
```
    homie/lightcontrol/lights/1/power/set 
```

To give an example: A lightcontrol device exposing the lights/1 node with
a settable power property subscribes to the topic for commands:
```
    homie/lightcontrol/lights/1/power/set ← "true"
```

In response the device will turn on the light and upon success update its power
property state accordingly:
```
    homie/lightcontrol/lights/1/power → "true"
```

Testing with mosquitto:
```
    mosquitto_sub -t "#" --debug
```
