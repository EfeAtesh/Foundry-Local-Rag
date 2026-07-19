import { useState } from 'react'
import { Send, Bot, User, Sparkles, Plus, MessageSquare, Settings } from 'lucide-react'
import './App.css'

function App() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Hello, just write a thing or ask any question to me, that you have...' }
  ])
  const [loading, setLoading] = useState(false)
  const [sessions, setSessions] = useState([
    { id: 1, title: 'New Chat', active: true }
  ])

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!input.trim()) return

    const userMessage = input
    
    setMessages((prevMessages) => [
      ...prevMessages,
      { role: 'user', text: userMessage }
    ])

    setInput('')
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: userMessage }),
      });

      const data = await response.json();

      setMessages((prevMessages) => [
        ...prevMessages,
        { role: 'assistant', text: data.response }
      ]);

    } catch (error) {
      console.error('ERROR:', error)
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: 'assistant', text: 'Something uncompatible occured' }
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="macos-window">
      {/* macOS Sidebar */}
      <aside className="sidebar">
        {/* Traffic Light Controls */}
        <div className="window-controls">
          <span className="control close"></span>
          <span className="control minimize"></span>
          <span className="control expand"></span>
        </div>

        <button className="new-chat-button">
          <Plus size={14} />
          <span>Set chat topic: </span>
        </button>

        <button className="new-chat-button">
          <Plus size={14} />
          <span>Set chat topic: </span>
        </button>

        <button className="new-chat-button">
          <Plus size={14} />
          <span>Set chat topic: </span>
        </button>




        

      </aside>
      {/* macOS Main Chat Area */}
      <main className="main-content">
        <header className="chat-header">
          <Sparkles className="header-icon" size={16} />
          <h2>Foundry Local RAG</h2>
        </header>

        {/* Message Window */}
        <div className="chat-window">
          {messages.map((msg, index) => (
            <div key={index} className={`message-row ${msg.role}`}>
              <div className="avatar">
                {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
              </div>
              <div className="message-bubble">
                <p>{msg.text}</p>
              </div>
            </div>
          ))}


          {/* Typing Loading Indicator */}
          {loading && (
            <div className="message-row assistant loading">
              <div className="avatar">
                <Bot size={14} />
              </div>
              <div className="message-bubble">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Floating Input Area */}
        <footer className="chat-input-area">
          <form onSubmit={handleSubmit} className="input-form">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Select here to type..."
              disabled={loading}
              className="chat-input"
            />
            <button type="submit" disabled={loading || !input.trim()} className="send-button">
              <Send size={14} />
            </button>
          </form>
        </footer>
      </main>
    </div>
  )
}

function setConvoTopic(index) {
  
  const [convoTopic1, setConvoTopic1] = useState("Wilderness Survival Guide")
  const [convoTopic2, setConvoTopic2] = useState("Vehicle Fixing Guide")
  const [convoTopic3, setConvoTopic3] = useState("Finding water or Setting Fire Guide")




}

  



export default App
