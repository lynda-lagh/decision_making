# 🌡️ Complete Sensor Data Specification

## 📊 **Total Sensors: 17 Sensors + 1 Anomaly Flag**

---

## **ORIGINAL SENSORS (6)**

### **1. Engine Temperature (°C)**
- **Range**: 20-150°C
- **Normal**: 60-90°C
- **Warning**: 90-110°C
- **Critical**: >110°C
- **Pattern**: Increases with load, seasonal variation
- **Anomaly**: Overheating (>110°C)

### **2. Vibration (mm/s)**
- **Range**: 0-15 mm/s
- **Normal**: 1.5-3.5 mm/s
- **Warning**: 3.5-5.0 mm/s
- **Critical**: >5.0 mm/s
- **Pattern**: Increases with degradation
- **Anomaly**: Sudden spikes (bearing failure, imbalance)

### **3. Oil Pressure (bar)**
- **Range**: 0-8 bar
- **Normal**: 3.5-5.5 bar
- **Warning**: 2.5-3.5 bar
- **Critical**: <2.5 bar
- **Pattern**: Decreases with degradation
- **Anomaly**: Sudden drops (oil leak, pump failure)

### **4. RPM (Revolutions Per Minute)**
- **Range**: 0-3000 RPM
- **Normal**: 1200-2200 RPM
- **Idle**: 800-1000 RPM
- **Max**: 2500-3000 RPM
- **Pattern**: Varies with load and work type
- **Anomaly**: Erratic behavior, stalling

### **5. Fuel Consumption (L/h)**
- **Range**: 0-30 L/h
- **Normal**: 10-20 L/h
- **Idle**: 2-5 L/h
- **Heavy Load**: 20-30 L/h
- **Pattern**: Increases with load and degradation
- **Anomaly**: Excessive consumption (fuel leak, inefficiency)

### **6. Engine Load (%)**
- **Range**: 0-100%
- **Normal**: 40-70%
- **Light Work**: 20-40%
- **Heavy Work**: 70-90%
- **Pattern**: Varies with work intensity
- **Anomaly**: Constant high load (overworking)

---

## **NEW SENSORS (11)**

### **7. Hydraulic Pressure (bar)**
- **Range**: 0-250 bar
- **Normal**: 120-180 bar
- **Warning**: 80-120 bar or 180-220 bar
- **Critical**: <80 bar or >220 bar
- **Purpose**: Monitor hydraulic system for implements
- **Pattern**: Decreases with degradation, varies with implement use
- **Anomaly**: Sudden drops (hydraulic leak, pump failure)
- **Critical for**: Plows, Cultivators, Balers, Harvesters

### **8. Battery Voltage (V)**
- **Range**: 10-14 V
- **Normal**: 12.4-13.2 V
- **Charging**: 13.5-14.5 V
- **Warning**: 11.5-12.4 V
- **Critical**: <11.5 V
- **Purpose**: Monitor electrical system health
- **Pattern**: Degrades over time, drops when not charging
- **Anomaly**: Sudden drops (alternator failure, battery degradation)

### **9. Coolant Temperature (°C)**
- **Range**: 20-120°C
- **Normal**: 70-95°C
- **Warning**: 95-105°C
- **Critical**: >105°C
- **Purpose**: Monitor cooling system
- **Pattern**: Related to engine temp (85% of engine temp)
- **Anomaly**: Overheating (coolant leak, radiator failure)

### **10. Air Filter Pressure (mbar)**
- **Range**: 0-200 mbar
- **Normal**: 20-80 mbar
- **Warning**: 80-150 mbar
- **Critical**: >150 mbar
- **Purpose**: Monitor air filter condition
- **Pattern**: Increases with dirt accumulation
- **Anomaly**: Rapid increase (dusty conditions, clogged filter)
- **Maintenance**: Replace filter when >150 mbar

### **11. Exhaust Temperature (°C)**
- **Range**: 100-800°C
- **Normal**: 300-500°C
- **Warning**: 500-650°C
- **Critical**: >650°C
- **Purpose**: Monitor combustion efficiency
- **Pattern**: 1.3x engine temperature
- **Anomaly**: Very high temps (combustion issues, turbo problems)

### **12. Transmission Temperature (°C)**
- **Range**: 30-120°C
- **Normal**: 60-90°C
- **Warning**: 90-105°C
- **Critical**: >105°C
- **Purpose**: Monitor transmission health
- **Pattern**: 90% of engine temperature
- **Anomaly**: Overheating (transmission fluid low, clutch problems)

### **13. Tire Pressure Front (PSI)**
- **Range**: 15-40 PSI
- **Normal**: 28-35 PSI
- **Warning**: 22-28 PSI or 35-38 PSI
- **Critical**: <22 PSI or >38 PSI
- **Purpose**: Monitor tire condition and safety
- **Pattern**: Decreases slowly with degradation
- **Anomaly**: Sudden drops (puncture, leak)

### **14. Tire Pressure Rear (PSI)**
- **Range**: 15-40 PSI
- **Normal**: 24-30 PSI
- **Warning**: 20-24 PSI or 30-35 PSI
- **Critical**: <20 PSI or >35 PSI
- **Purpose**: Monitor rear tire condition
- **Pattern**: Decreases slowly with degradation
- **Anomaly**: Sudden drops (puncture, leak)

### **15. GPS Speed (km/h)**
- **Range**: 0-30 km/h
- **Normal**: 5-15 km/h (working)
- **Transport**: 15-30 km/h
- **Idle**: 0 km/h
- **Purpose**: Monitor movement and work patterns
- **Pattern**: Zero at night, varies during work hours
- **Anomaly**: Excessive speed (unsafe operation)

### **16. Working Hours (hours)**
- **Range**: 0-50,000 hours
- **Purpose**: Track cumulative equipment usage
- **Pattern**: Increases linearly over time
- **Use**: Maintenance scheduling, depreciation
- **Critical**: Trigger maintenance at intervals (500h, 1000h, etc.)

### **17. Fuel Level (%)**
- **Range**: 0-100%
- **Normal**: 20-100%
- **Warning**: 10-20%
- **Critical**: <10%
- **Purpose**: Monitor fuel status
- **Pattern**: Decreases during work, refills randomly
- **Anomaly**: Rapid decrease (fuel leak)

---

## **18. Anomaly Flag (Binary)**
- **Values**: 0 (Normal) or 1 (Anomaly)
- **Triggers**: 
  - Temperature spike (>15°C increase)
  - Vibration spike (>3 mm/s increase)
  - Oil pressure drop (>1 bar decrease)
  - Coolant temperature spike (>20°C increase)
  - Battery voltage drop (>1V decrease)
- **Frequency**: 3% of readings (realistic anomaly rate)
- **Purpose**: Pre-labeled data for anomaly detection training

---

## 📈 **Sensor Patterns**

### **Daily Patterns:**
```
06:00-18:00: Work hours
- Higher temperatures
- Higher RPM
- Higher fuel consumption
- Higher engine load
- GPS speed > 0

18:00-06:00: Idle/Off
- Lower temperatures
- Zero or idle RPM
- Minimal fuel consumption
- Zero engine load
- GPS speed = 0
```

### **Seasonal Patterns:**
```
Summer (Jun-Aug):
- Higher temperatures (+15%)
- More cooling system stress
- Higher exhaust temps

Winter (Dec-Feb):
- Lower temperatures (-10%)
- Longer warm-up times
- Better cooling efficiency

Spring/Fall:
- Normal temperatures
- Optimal operating conditions
```

### **Degradation Patterns:**
```
Over 5 years (2020-2025):
- Temperature: +40% increase
- Vibration: +40% increase
- Oil pressure: -50% decrease
- Battery voltage: -40% decrease
- Air filter pressure: +300% increase
- Tire pressure: -10% decrease
- Fuel consumption: +20% increase
```

---

## 🎯 **Use Cases for Each Sensor**

### **Predictive Maintenance:**
1. **Temperature + Vibration** → Bearing failure prediction
2. **Oil Pressure + Temperature** → Engine wear prediction
3. **Air Filter Pressure** → Filter replacement scheduling
4. **Battery Voltage** → Battery replacement prediction
5. **Tire Pressure** → Tire maintenance scheduling
6. **Hydraulic Pressure** → Hydraulic system maintenance

### **Anomaly Detection:**
1. **Temperature Spikes** → Overheating events
2. **Vibration Spikes** → Mechanical issues
3. **Pressure Drops** → Leaks or pump failures
4. **Battery Drops** → Electrical problems
5. **Coolant Spikes** → Cooling system failures

### **Performance Monitoring:**
1. **Fuel Consumption + Engine Load** → Efficiency analysis
2. **GPS Speed + Working Hours** → Productivity tracking
3. **RPM + Engine Load** → Optimal operation analysis
4. **Exhaust Temperature** → Combustion efficiency

### **Safety Monitoring:**
1. **Tire Pressure** → Safety alerts
2. **GPS Speed** → Speed limit enforcement
3. **Fuel Level** → Refueling alerts
4. **Battery Voltage** → Starting reliability

---

## 📊 **Data Volume**

### **Per Equipment:**
```
Sensors: 17 + 1 anomaly flag = 18 data points
Frequency: Hourly
Period: 5 years (2020-2025)
Readings: 43,800 hours × 18 sensors = 788,400 data points per equipment
```

### **Total Dataset (300 equipment):**
```
Total readings: 13,140,000 rows
Total data points: 236,520,000 values
Storage: ~5-10 GB (depending on compression)
```

### **Time Series Ready:**
```
Monthly aggregation: 60 months × 18 sensors = 1,080 points per equipment
Daily aggregation: 1,825 days × 18 sensors = 32,850 points per equipment
Hourly: 43,800 hours × 18 sensors = 788,400 points per equipment
```

---

## 🔧 **Feature Engineering Opportunities**

### **From Sensors:**
1. **Temperature Gradient** = (Current Temp - Previous Temp) / Time
2. **Vibration Trend** = Rolling average (7 days, 30 days)
3. **Pressure Drop Rate** = Change in pressure over time
4. **Battery Health Index** = Voltage / Expected Voltage
5. **Filter Clogging Rate** = Air filter pressure increase rate
6. **Tire Wear Rate** = Pressure decrease rate
7. **Fuel Efficiency** = Fuel consumption / Engine load
8. **Thermal Efficiency** = Exhaust temp / Engine temp
9. **Hydraulic Health** = Hydraulic pressure / Expected pressure
10. **Overall Health Score** = Weighted combination of all sensors

### **Cross-Sensor Features:**
1. **Temp-Vibration Correlation** → Bearing health
2. **Pressure-Temperature Ratio** → Engine efficiency
3. **Load-Consumption Ratio** → Fuel efficiency
4. **Speed-Load Correlation** → Work pattern
5. **Battery-Temperature Correlation** → Electrical health

---

## ✅ **Benefits of Extended Sensor Set**

### **For ML Models:**
- ✅ 18 features instead of 6 (3x increase)
- ✅ Richer patterns for learning
- ✅ Better failure prediction
- ✅ More accurate anomaly detection

### **For Time Series:**
- ✅ Multiple correlated signals
- ✅ Better trend detection
- ✅ More robust forecasting
- ✅ Cross-validation opportunities

### **For Thesis:**
- ✅ Comprehensive IoT monitoring
- ✅ Real-world relevance
- ✅ Multiple research angles
- ✅ Publication-worthy depth

### **For Industry:**
- ✅ Production-ready monitoring
- ✅ Complete equipment health picture
- ✅ Actionable maintenance insights
- ✅ Safety compliance

---

## 🚀 **Ready to Generate!**

```bash
cd scripts
python fix_data_issues.py
```

**This will create:**
- ✅ 300 equipment (14 types)
- ✅ 28 Tunisian locations
- ✅ **18 sensors per equipment** (6 original + 11 new + 1 anomaly flag)
- ✅ 13,140,000 sensor readings
- ✅ 236,520,000 data points!
- ✅ 5 years of temporal data (2020-2025)
- ✅ Perfect for advanced ML and time series!

**Your dataset is now WORLD-CLASS!** 🌍🎓
