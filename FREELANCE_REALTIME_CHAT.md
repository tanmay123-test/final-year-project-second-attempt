# Freelance Real-time Communication

This document describes the real-time communication feature implemented for the freelance module.

## Overview

The freelance module now supports real-time messaging between clients and freelancers using Socket.io. This enables instant communication within active projects, improving collaboration and project management.

## Features

### ✅ Implemented Features

- **Real-time Messaging**: Instant message delivery between project participants
- **Online Status**: See who's currently online in the project
- **Typing Indicators**: Know when someone is typing a message
- **Read Receipts**: Mark messages as read
- **File Sharing**: Share files in chat (basic implementation)
- **Connection Status**: Visual indicators for connection status
- **Responsive Design**: Works on desktop and mobile devices

### 🔧 Technical Implementation

#### Backend Components

1. **Socket Handlers** (`backend/services/freelance/socket_handlers.py`)
   - Handles WebSocket connections for freelance projects
   - Manages room-based communication
   - Tracks online users and typing indicators

2. **Database Schema** (`backend/services/freelance/models/database.py`)
   - Added `is_read` column to `freelance_messages` table
   - PostgreSQL-based storage for message persistence

3. **Integration** (`backend/app.py`)
   - Socket handlers registered with main SocketIO instance
   - No impact on other modules

#### Frontend Components

1. **Socket Service** (`frontend/src/services/freelance/freelanceSocket.js`)
   - Manages WebSocket connections
   - Handles real-time events
   - Provides clean API for components

2. **Chat Component** (`frontend/src/services/freelance/components/RealTimeChat.jsx`)
   - Complete chat interface
   - Real-time message display
   - Typing indicators and online status

3. **Integration Points**
   - Project Detail Page: Chat appears for projects in progress
   - Freelancer Work Page: Enhanced messaging for active work

## How to Use

### For Clients

1. **Post a Project**: Create a project on the freelance platform
2. **Receive Proposals**: Review proposals from freelancers
3. **Accept Proposal**: Start the project by accepting a proposal
4. **Access Chat**: Go to project details → "Project Chat" section
5. **Start Communicating**: Send messages and share files with the freelancer

### For Freelancers

1. **Find Projects**: Browse available projects
2. **Submit Proposals**: Apply for projects that match your skills
3. **Get Hired**: Wait for client to accept your proposal
4. **Access Chat**: Go to "My Work" → Select active project → "Project Chat"
5. **Collaborate**: Communicate with client in real-time

### Chat Features

- **Send Messages**: Type and send messages instantly
- **Share Files**: Click the paperclip icon to share files
- **See Online Status**: Green dot shows who's online
- **Typing Indicators**: See when someone is typing
- **Message History**: All messages are saved and displayed

## Technical Details

### Socket Events

| Event | Description | Data |
|-------|-------------|------|
| `join_freelance_project` | Join a project chat room | `{project_id, user_id}` |
| `leave_freelance_project` | Leave a project chat room | `{project_id, user_id}` |
| `send_freelance_message` | Send a message | `{project_id, sender_id, message, file_attachment}` |
| `typing_start` | Start typing indicator | `{project_id, user_id}` |
| `typing_stop` | Stop typing indicator | `{project_id, user_id}` |
| `get_online_users` | Get online users list | `{project_id}` |
| `mark_messages_read` | Mark messages as read | `{project_id, user_id}` |

### Database Schema

```sql
-- Updated freelance_messages table
CREATE TABLE freelance_messages (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    contract_id INTEGER,
    sender_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    file_attachment TEXT,
    is_read BOOLEAN DEFAULT FALSE,  -- New column
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES freelance_projects (id),
    FOREIGN KEY (contract_id) REFERENCES freelance_contracts (id)
);
```

## Testing

### Automated Tests

Run the test script to verify functionality:

```bash
cd backend
python test_freelance_socket.py
```

### Manual Testing

1. **Start Backend**: `python app.py`
2. **Start Frontend**: `npm run dev` (in frontend directory)
3. **Create Test Project**: Post a freelance project
4. **Accept Proposal**: Start a contract
5. **Test Chat**: Send messages and verify real-time updates

### Debugging

- **Browser Console**: Check for socket connection status
- **Network Tab**: Monitor WebSocket connections
- **Backend Logs**: Watch for socket event logs

## Configuration

### Environment Variables

Ensure these are set in your `.env` file:

```env
DATABASE_URL=postgresql://username:password@host:port/database
```

### CORS Settings

Socket.io is configured to work with:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:5174`
- `http://localhost:5175`
- `http://127.0.0.1:5173`
- `http://127.0.0.1:5174`
- `http://127.0.0.1:5175`

## Troubleshooting

### Common Issues

1. **Socket Not Connecting**
   - Check if backend server is running
   - Verify CORS settings
   - Check browser console for errors

2. **Messages Not Sending**
   - Verify user authentication
   - Check project status (must be 'IN_PROGRESS')
   - Check database connection

3. **Online Status Not Working**
   - Ensure user has joined the project room
   - Check WebSocket connection stability

### Performance Considerations

- Messages are stored in PostgreSQL for persistence
- Online users are stored in memory (cleared on server restart)
- File uploads are basic (consider cloud storage for production)

## Future Enhancements

### Planned Features

- **File Upload Integration**: Proper file storage system
- **Message Reactions**: Emoji reactions to messages
- **Message Editing**: Edit sent messages
- **Message Deletion**: Delete messages with permissions
- **Push Notifications**: Browser notifications for new messages
- **Chat History Search**: Search through message history
- **Voice Messages**: Send voice recordings
- **Video Chat Integration**: Direct video calling from chat

### Scalability Improvements

- **Redis Integration**: For better socket state management
- **Message Queuing**: For high-volume messaging
- **Load Balancing**: Multiple socket server instances
- **Database Optimization**: Message indexing and archiving

## Support

If you encounter issues:

1. Check the browser console for JavaScript errors
2. Verify backend logs for socket connection issues
3. Ensure database is accessible and schema is up to date
4. Test with the provided test script

## Security Notes

- All socket connections require valid user authentication
- Messages are validated before storage
- File uploads should be validated in production
- Consider rate limiting for message sending

---

**Last Updated**: March 26, 2026  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
