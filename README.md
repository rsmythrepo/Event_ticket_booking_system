# Event ticket booking system

### Overview
An Event Ticket Booking System that allows users to browse, search, and book tickets for a variety of entertainment events such as concerts, sports games, movies, or theater shows. The system should also include features for event management, ticket availability tracking, seat selection, and payment processing.

### Key Features
- User Authentication: Secure user registration, login, and profile management.
- Event Browsing & Search: Users can browse events by category, search based on date, venue, or price, and filter events for an optimized experience.
- Seat Selection: Interactive seat selection feature for events with reserved seating.
- Ticket Booking: Simple ticket booking process with an integrated payment system.
- Admin Dashboard: Admins can create and manage events, view sales analytics, and handle cancellations or refunds.
- Notifications: Automatic email notifications for booking confirmations, cancellations, and promotions.
- Dynamic Pricing: Support for different ticket tiers with varying prices.
- Payment Processing: Secure payment handling with the ability to save payment details.

### Technology Stack
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

### Installation & Setup
#### Prerequisites
Docker installed and running

Python 3.9+ and pip (for local development)

MySQL server setup (local or cloud-based)

#### Local Development
Clone the repository: git clone https://github.com/rsmythrepo/Event_ticket_booking_system.git

cd Event_ticket_booking_system

Install dependencies: pip install -r requirements.txt

Set up environment variables: setx ENCRYPTION_KEY "crypto-key"

### Run the application
python run.py

Access the app: Visit http://localhost:5000 in your web browser.

#### Local Docker Deployment
Build and run the containers: docker-compose up --build

Access the app: Visit the server IP or http://localhost:5000.

#### EC2 Docker Deployemt 
Connect to Your EC2 Instance: ssh -i /path/to/your-key.pem ec2-user@your-ec2-public-ip

Update the System Packages: sudo yum update -y

Install Docker: sudo yum install -y docker

sudo service docker start

sudo systemctl enable docker

Install Docker Compose: sudo curl -L "https://github.com/docker/compose/releases/download/$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -Po '"tag_name": "\K[0-9.]+')" /docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose

Build Dockerfile: sudo docker-compose up --build -d

Show Containers: sudo docker ps

Security Group: You will need to create an inbound rule under the EC2 security groups: Custom TCP, TCP, 5000, Anywhere (0.0.0.0/0)

Access from EC2:  http://<EC2_PUBLIC_IP>:5000

### Database Design 
Below is the ER diagram for the Event Ticket Booking System:

![ER Diagram](database_setup/ER_Diagram.png)



### Contributors:
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














  




