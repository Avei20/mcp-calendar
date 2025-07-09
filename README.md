# Google Calendar MCP Server (Vibe Code using Zed)

## Requirements
1. Integration with Google Calendar
2. Connect to a database to store token, use sqlalchemy to connect.
3. Must be deployed in Cloud Run. The connection will using remote mcp.
4. The functionality is
  - Get The Calendar
  - Create The Calendar
  - Update The Calendar
  - Delete a Caledar
5. Fulfill the requirement first. Lates do the improvement.

### Future Improvement.
1. Connect to Google Task to convert the event into task if has passed.
2. Connect to Other Google Workspaces such as, Gmail, Notes, Docs, Sheet, etc.
