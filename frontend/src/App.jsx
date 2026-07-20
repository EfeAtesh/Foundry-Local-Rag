import { useState } from 'react'
import { Send, Bot, User, Sparkles, Plus, MessageSquare, Settings } from 'lucide-react'
import './App.css'



//main application component representing the local rag user interface
function App() {
  //state to keep track of the text inputted in the search/chat input
  const [input, setInput] = useState('')
  //state storing the array of message objects to render in the chat window
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Hello, just write a thing or ask any question to me, that you have...' }
  ])
  //state representing the loading status during chat api calls
  const [loading, setLoading] = useState(false)
  //state for managing user conversation sessions
  const [sessions, setSessions] = useState([
    { id: 1, title: 'New Chat', active: true }
  ])

  //state indicating the currently active specialized manual topic
  const [convoTopic, setConvoTopic] = useState(0)

  //handles client side submit, appends suffix for active topic guide, and fetches response from fastapi backend
  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!input.trim()) return

    let userMessage = input.trim()

    if (convoTopic === 1){
      userMessage += "é*:1"
    }
    else if (convoTopic === 2){
      userMessage += "é*:2"
    }
    else if (convoTopic === 3){
      userMessage += "é*:3"
    }
    
    setMessages((prevMessages) => [
      ...prevMessages,
      { role: 'user', text: input.trim() }
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
      const botResponse = data.response || 'Errorr.';


      setMessages((prevMessages) => [
        ...prevMessages,
        { role: 'assistant', text: '' }
      ]);

      let index = 0;
      
      //simulates real time streaming effect by flushing response characters sequentially
      const fakeFlush = setInterval(() => {
        
        if (index < botResponse.length){
          setMessages((prevMessages) => [...prevMessages.slice(0, -1), { role: 'assistant', text: botResponse.slice(0, index + 1) }])
          index++;
        }
        else {
          clearInterval(fakeFlush);
        }
      
        },2.22);

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
      {/*macos sidebar*/}
      <aside className="sidebar">
        {/*traffic light controls*/}
        <div className="window-controls">
          <span className="control close"></span>
          <span className="control minimize"></span>
          <span className="control expand"></span>
        </div>

        <button 
          className={`new-chat-button ${convoTopic === 3 ? 'active' : ''}`} 
          onClick={() => setConvoTopic(prev => prev === 3 ? 0 : 3)}
        >
          <Plus size={14} />
          <span>Set chat topic: Wilderness Survival Guide</span>
        </button>

        <button 
          className={`new-chat-button ${convoTopic === 1 ? 'active' : ''}`} 
          onClick={() => setConvoTopic(prev => prev === 1 ? 0 : 1)}
        >
          <Plus size={14} />
          <span>Set chat topic: Vehicle Fixing Guide</span>
        </button>

        <button 
          className={`new-chat-button ${convoTopic === 2 ? 'active' : ''}`} 
          onClick={() => setConvoTopic(prev => prev === 2 ? 0 : 2)}
        >
          <Plus size={14} />
          <span>Set chat topic: Finding water or Setting Fire Guide</span>
        </button>




        

      </aside>
      {/*macos main chat area*/}
      <main className="main-content">
        <header className="chat-header">
          <Sparkles className="header-icon" size={16} />
          <h2>Foundry Local RAG Project from Microsoft Summer School 2026: Quick Techincal Help</h2>
        </header>

        {/*message window*/}
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


          {/*typing loading indicator*/}
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

        {/*floating input area*/}
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







export default App
