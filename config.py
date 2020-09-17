# Šeti norāda Beckhoff Modbus/TCP kontrolieru IP adreses un to nosaukumus
controllers = {
    'warehouse': '192.168.200.104',
    'office': '192.168.200.129'
}
# Mqtt servera IP adrese
mqtt_host = '127.0.0.1'
mqtt_port = 1883
mqtt_controller_name = 'lightcontrol'

# Laiks sekundēs starp impulsa slēdža ieslēgšanu un izslēgšanu
toggle_time = 0.25

# Log level var būt DEBUG, INFO, WARNING, ERROR, CRITICAL
log_level = "DEBUG"
log_format="%(asctime)s:%(name)s:%(levelname)s:%(message)s"
