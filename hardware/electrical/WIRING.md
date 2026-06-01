# CHORUS-SGH-1 Electrical / DAQ Wiring

## Sensor map

| Signal | Sensor | Interface | Pi channel |
|--------|--------|-----------|------------|
| P_feed | 0–40 bar transducer | 4–20 mA → 250Ω | MCP3008 CH0 |
| P_draw | 0–40 bar transducer | 4–20 mA → 250Ω | CH1 |
| Q_feed | turbine flow | pulse / analog | CH2 |
| Q_draw | turbine flow | pulse / analog | CH3 |
| cond_feed | conductivity cell | analog board | CH4 |
| cond_draw | conductivity cell | analog board | CH5 |
| T_feed | NTC 10k | divider | CH6 |
| T_draw | NTC 10k | divider | CH7 |

## AEH harvest bus

```
Piezo array → bridge rectifier → supercap 5F → buck 5V → Pi USB (optional)
```

## Ultrasonic driver (isolated from harvest)

```
Sig gen 28 kHz → MOSFET driver → US transducer 50W max
Enable interlock with P_draw > threshold
```

## Pump interlock

```
Draw pressure OK + feed flow OK → enable feed pump relay
E-stop cuts all pumps + US
```

See `WIRING_DIAGRAM.txt` for ASCII layout.
