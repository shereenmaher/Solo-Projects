# 🚢 Where's My Box?

**Import Shipment Management Made Simple**

Where's My Box? is a web application designed for **import companies** to manage incoming container shipments from one place.

Instead of only answering **"Where is my container?"**, the application helps importers answer three important questions:

- 📍 **Where is my shipment?**
- 📄 **Are the required documents ready?**
- 💰 **What did the shipment really cost?**

The goal is to bring shipment tracking, document readiness, and landed cost management together in one simple dashboard.

---

## ✨ Main Features

### 🚢 Container Tracking
- Add shipments using a container number
- Track shipment status
- View ETA and ATA
- View origin and destination
- View vessel information
- View shipment event history
- Manually refresh tracking information
- Automatically check shipments at regular intervals
- Detect important shipment and ETA changes

### 📄 Document Readiness
Track the documents required for an incoming shipment, including:

- Commercial Invoice
- Packing List
- Bill of Lading
- Certificate of Origin
- Insurance
- Customs Declaration

The application calculates a **document readiness percentage** and helps identify missing documents before the shipment arrives.

### 💰 Landed Cost Tracker
Calculate the true cost of an imported shipment using:

- Goods Value
- Ocean Freight
- Customs / Duties
- Insurance
- Local Transportation
- Other Costs
- Quantity

The system calculates:

**Total Landed Cost**

and

**Landed Cost Per Unit**

---

## 🔄 How It Works

1. The user creates an account and logs in.
2. A shipment is added using its container number.
3. The application requests tracking information from the Traqo API.
4. Shipment information is stored in the database.
5. Users can monitor shipment status and history.
6. Important tracking changes can trigger email notifications.
7. Users can manage shipment document readiness.
8. Users can enter shipment expenses and calculate landed cost.

---

## 🛠️ Technologies Used

### Backend
- Python
- Django
- Django ORM

### Frontend
- HTML5
- CSS3
- Django Templates

### Database
- SQLite

### API
- Traqo Ocean Container Tracking API

### Other Tools
- Git
- GitHub
- VS Code
- bcrypt for password hashing

---

## 🔗 API Integration

Where's My Box? integrates with the **Traqo Ocean API** to retrieve container tracking information.

Tracking data includes information such as:

- Shipment status
- Estimated Time of Arrival (ETA)
- Actual Time of Arrival (ATA)
- Origin
- Destination
- Vessel information
- Shipment events

---

## 🔔 Shipment Monitoring

Shipments can be refreshed manually, while the application is also designed to check shipment information automatically at regular intervals.

When important information changes, such as the shipment status or ETA, the system can notify the user by email.

---

## 🎯 Target Users

Where's My Box? is designed primarily for:

**Import companies and businesses managing incoming container shipments.**

The application is not intended to replace shipping lines or freight forwarders. Instead, it helps the **importer** organize and understand the information surrounding an incoming shipment.

---

## 💡 Why Where's My Box?

Container tracking platforms usually focus on one question:

> **Where is my container?**

Where's My Box? expands that into three:

> 📍 **Where is it?**  
> 📄 **Are we ready for it?**  
> 💰 **What did it cost us?**

**Tracking. Documents. Costs. One place.**

---

## 🚀 Future Improvements

Possible future features include:

- Demurrage and free-time risk monitoring
- More advanced shipment alerts
- Inventory and stock-out risk calculations
- Additional shipping API integrations
- Improved reporting and analytics
- Cloud deployment

---

## 👩‍💻 Project

Developed as a Full-Stack Development project at **AXSOS Academy**.
