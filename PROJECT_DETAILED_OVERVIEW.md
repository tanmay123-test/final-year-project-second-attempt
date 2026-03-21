# **Expertease: A Multi-Service Ecosystem**

## **Project Purpose & Architecture**
Expertease is a comprehensive, multi-service platform designed to streamline daily needs through a unified digital interface. It acts as a bridge between service seekers and providers across diverse domains including healthcare, automobile maintenance, financial management, freelance work, and housekeeping.

**Architecture Overview:**
- **Frontend**: A modular React application built with **Vite**, utilizing **React Router** for navigation and **Context API** for global state management (Authentication and Notifications).
- **Backend**: A robust **Python Flask** server structured with a blueprint-based modular architecture, allowing independent scaling and maintenance of different service modules.
- **Database**: Multiple **SQLite** databases distributed across modules to ensure data isolation and integrity, with **SQLAlchemy** (in some parts) for ORM capabilities.
- **AI Integration**: Leverages **Google Gemini AI** for intelligent features like financial coaching, AI mechanic assistance, and automated housekeeping advisors.

---

## **Core Features**

### **1. Car Service & Automobile Expert**
- **AI Mechanic**: Diagnostic assistance powered by AI.
- **On-Demand Services**: Fuel delivery, tow truck booking, and mechanic appointments.
- **Expert Consultations**: Real-time video/chat consultations with automobile experts.
- **Worker Dashboards**: Specialized interfaces for mechanics and delivery operators to manage jobs and earnings.

### **2. Finny: Smart Financial Management**
- **Transaction Tracking**: Automated and manual expense logging.
- **AI Financial Coach**: Personalized financial advice and analytics using Gemini.
- **Visual Analytics**: Interactive charts and category breakdowns for spending habits.

### **3. Freelance Marketplace**
- **Client Flow**: Project posting, freelancer discovery, and proposal management.
- **Worker Flow**: Project bidding, portfolio management, and secure wallet system.
- **Collaboration**: Integrated communication tools for project discussion.

### **4. Healthcare System**
- **Doctor Discovery**: Search by specialization and availability.
- **Booking Engine**: Seamless appointment scheduling.
- **Consultation**: Video-based remote consultations.

### **5. Housekeeping & Arrival**
- **Booking Flow**: Streamlined scheduling for household services.
- **Provider Management**: Availability scheduling and earnings tracking for service providers.
- **AI Advisor**: Intelligent assistant for housekeeping queries.

---

## **File Structure & Directory Map**

```text
/final-year-project-second-attempt
├── backend/                  # Flask Server Application
│   ├── admin/                # Global admin controls
│   ├── ai/                   # Core AI logic (Gemini clients, vector stores)
│   ├── car_service/          # Car-related service modules (Mechanic, Tow, etc.)
│   ├── housekeeping/         # Housekeeping service logic
│   ├── services/             # Specialized services (Freelance, Money, Video)
│   ├── app.py                # Main entry point and blueprint registration
│   └── *.db                  # Distributed SQLite database files
├── frontend/                 # React Client Application
│   ├── src/
│   │   ├── components/       # Reusable UI components (Navbars, Modals)
│   │   ├── context/          # State management (Auth, Toast)
│   │   ├── pages/            # Core landing and dashboard pages
│   │   ├── services/         # Domain-specific modules (Car, Finny, Healthcare)
│   │   ├── shared/           # Common logic and styles across modules
│   │   ├── App.jsx           # Main routing and application structure
│   │   └── main.jsx          # Vite entry point
│   └── vite.config.js        # Build configuration
```

---

## **Data Flow**

1. **User Interaction**: Users interact with the React frontend, which triggers state updates via Context API or local state.
2. **API Layer**: Frontend makes asynchronous requests to the Flask backend using `fetch` or `axios`.
3. **Backend Processing**: 
   - Requests are routed through Flask Blueprints to specific service controllers.
   - Authentication is verified using JWT/Token-based logic.
   - AI-related requests are forwarded to the `ai` module, which communicates with the Gemini API.
4. **Persistence**: Data is read from or written to the respective SQLite database files.
5. **Real-time Updates**: Real-time features (like video signaling) use **Socket.io** for low-latency communication between the client and server.

---

## **User Interface Design**

**Philosophy**: Minimalist, Modern, and Service-Oriented.
- **Thematic Consistency**: Uses CSS variables (defined in `index.css`) for a uniform color palette.
- **Service Identity**: Each service has its own "color language" (e.g., `--medical-gradient` for healthcare).
- **Responsive Layout**: Designed with a mobile-first approach, utilizing modern CSS techniques (Flexbox, Grid) and modular navigation bars (e.g., `BottomNav.jsx`).
- **Modern Interactions**: Clean transitions and card-based layouts for high readability and ease of use.

---

## **Key Dependencies**

### **Frontend**
- `react` & `react-router-dom`: Core UI and navigation.
- `socket.io-client`: Real-time communication.
- `lucide-react`: Modern icon set.
- `framer-motion`: Smooth UI animations.
- `recharts`: Data visualization for Finny.

### **Backend**
- `flask` & `flask-cors`: Web framework and cross-origin support.
- `flask-socketio`: Real-time event handling.
- `google-generativeai`: Integration with Gemini AI.
- `razorpay`: Payment gateway integration.
- `sqlite3`: Lightweight data persistence.

---

## **Entry Points & Setup**

### **Backend Setup**
1. Navigate to `/backend`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the server: `python app.py`.
4. The server starts on `http://localhost:5000` (default).

### **Frontend Setup**
1. Navigate to `/frontend`.
2. Install dependencies: `npm install`.
3. Start development server: `npm run dev`.
4. Access the app via `http://localhost:5173`.

---

## **Recommendations & Improvements**

### **Recommendations**
- **Unified Database**: Consider migrating to a centralized PostgreSQL database for better scalability and complex queries as the project grows.
- **State Management**: As complexity increases, migrating from Context API to Redux Toolkit or Zustand might provide better debugging tools.
- **Containerization**: Use Docker to simplify setup for new developers by bundling both frontend and backend.

### **Improvement List**
- [ ] **Security**: Implement more robust rate-limiting on API endpoints.
- [ ] **Testing**: Increase coverage for backend services using `pytest`.
- [ ] **AI Performance**: Implement caching for AI responses to reduce latency and API costs.
- [ ] **UI/UX**: Add a global dark mode toggle (currently theme variables are defined but logic needs unification).
- [ ] **Documentation**: Generate Swagger/OpenAPI documentation for the backend endpoints.
