# 🎟️ Event Ticket Booking System

### 📝 Overview
An Event Ticket Booking System that allows users to browse, search, and book tickets for a variety of entertainment events such as concerts, sports games, movies, or theater shows. The system includes features for event management, ticket availability tracking, seat selection, and payment processing.

### 🌟 Key Features
- 🔒 **User Authentication**: Secure user registration, login, and profile management.
- 🔍 **Event Browsing & Search**: Browse events by category and search based on date, venue, or price.
- 🪑 **Seat Selection**: Interactive seat selection for reserved seating.
- 🎫 **Ticket Booking**: Simplified ticket booking with integrated payment.
- 🛠️ **Admin Dashboard**: Create/manage events, view analytics, and handle cancellations or refunds.
- 📧 **Notifications**: Automated email notifications for booking confirmations, cancellations, and promotions.
- 💰 **Dynamic Pricing**: Different ticket tiers with variable pricing.
- 💳 **Payment Processing**: Secure payments with the option to save payment details.

### 🛠️ Technology Stack
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Flask-SQLAlchemy](https://img.shields.io/badge/Flask--SQLAlchemy-DA291C?style=for-the-badge&logo=python&logoColor=white)
![Flask-Mail](https://img.shields.io/badge/Flask--Mail-000000?style=for-the-badge&logo=flask&logoColor=white)
![Cryptography](https://img.shields.io/badge/Cryptography-6A5ACD?style=for-the-badge&logo=python&logoColor=white)
![Bash](https://img.shields.io/badge/Bash-4EAA25?style=for-the-badge&logo=gnu-bash&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

---

## 🗃️ Database Design
Below is the ER diagram for the Event Ticket Booking System:

![ER Diagram](database_setup/ER_Diagram.png)

| Table Name        | Description                                                                                     |
|-------------------|-------------------------------------------------------------------------------------------------|
| role              | Stores user roles with unique role IDs and role names.                                          |
| user              | Holds user information including names, emails, passwords, and associated roles.                |
| event             | Contains details of events including title, venue, dates, and ticket availability.              |
| booking           | Represents user bookings for events, including total amount and status.                         |
| ticket_tier       | Defines different ticket tiers and their prices.                                                |
| event_ticket_tier | Links events to ticket tiers, specifying total tickets per tier.                                |
| seat              | Lists seats for events, indicating tier, availability, and unique seat numbers.                 |
| booking_seat      | Maps seats to bookings to track reserved seats for each booking.                                |
| ticket            | Represents tickets issued for bookings, including event, seat, and tier information.            |
| notification      | Stores notifications sent to users related to events, including status and type.                |
| payment_detail    | Contains payment details for users, such as card type and billing information.                  |
| payment           | Tracks payments for bookings, including amount, status, and associated payment details.         |

---

## 🚀 Installation & Setup
### Prerequisites
- 🐋 **Docker** installed and running
- 🐍 **Python 3.9+** and pip (for local development)
- 🗃️ **MySQL server** setup (local or cloud-based)

## 💻 Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rsmythrepo/Event_ticket_booking_system.git
   cd Event_ticket_booking_system
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   setx ENCRYPTION_KEY "crypto-key"
   ```

4. **Run the application:**
   ```bash
   python run.py
   ```

5. **Access the app:**
   Open [http://localhost:5000](http://localhost:5000) in your web browser.

---

## 🐳 Local Docker Deployment

1. **Build and run the containers:**
   ```bash
   docker-compose up --build
   ```

2. **Access the app:**
   Visit [http://localhost:5000](http://localhost:5000).

---

## ☁️ EC2 Docker Deployment

1. **Connect to Your EC2 Instance:**
   ```bash
   ssh -i /path/to/your-key.pem ec2-user@your-ec2-public-ip
   ```

2. **Update the system packages:**
   ```bash
   sudo yum update -y
   ```

3. **Install Docker:**
   ```bash
   sudo yum install -y docker
   sudo service docker start
   sudo systemctl enable docker
   ```

4. **Install Docker Compose:**
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/download/$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -Po '"tag_name": "\K[0-9.]+')" /docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

5. **Build and run the containers:**
   ```bash
   sudo docker-compose up --build -d
   ```

6. **Show running containers:**
   ```bash
   sudo docker ps
   ```

7. **Configure Security Group:**
   Create an inbound rule under the EC2 security groups:
   - **Type**: Custom TCP
   - **Protocol**: TCP
   - **Port Range**: 5000
   - **Source**: Anywhere (0.0.0.0/0)

8. **Access the app from EC2:**
   Open [http://<EC2_PUBLIC_IP>:5000](http://<EC2_PUBLIC_IP>:5000) in your web browser.

---

## 🤝 Contributors
<table>
  <tr>
    <td align="center">
      <a href="https://github.com/rsmythrepo">
        <img src="https://github.com/rsmythrepo.png" width="100px;" alt="Raphaelle Smyth"/><br />
        <sub><b>Raphaelle Smyth</b></sub>
    </td>
    <td align="center">
      <a href="https://github.com/AskhatBissembay">
        <img src="https://github.com/AskhatBissembay.png" width="100px;" alt="Askhat Bissembay"/><br />
        <sub><b>Askhat Bissembay</b></sub>
    </td>
    <td align="center">
      <a href="https://github.com/Vikiyuk">
        <img src="https://github.com/Vikiyuk.png" width="100px;" alt="Yurii Maisuradze"/><br />
        <sub><b>Yurii Maisuradze</b></sub>
    </td>
  </tr>
</table>














  




