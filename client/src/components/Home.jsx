import React, { useState } from 'react'
import axios from "axios"
import Loading from './Loading';

const Home = () => {
  const [pdfData, setPdfData] = useState(null);
  const [question, setQuestion] = useState('');
  const [isIngested, setIsIngested] = useState(false);
  const [isLoading, setIsLoading] = useState(false)
  const [ans, setAns] = useState('');
  const [ingestedFileName, setIngestedFileName] = useState('');

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    
    if (name === 'updf') {
      const file = files[0];
      setPdfData(file);
      setIsIngested(false);
      setIngestedFileName('');
      setAns('');
    } else if (name === 'ques') {
      setQuestion(value);
    }
  }

  const handleIngest = async() => {
    if(!pdfData){
      alert("Upload pdf first")
      return
    }
    setIsLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', pdfData)
      const response = await axios.post("http://127.0.0.1:8000/ingest", formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      if(response.data.status == "success"){
        alert("File Ingested successfully")
        setIsIngested(true)
        setIngestedFileName(response.data.data.filename);
      }
      else{
        alert("An error occurred: " + response.data.message)
        console.log(response.data.message)
      }
    } catch (error) {
      alert("An error occurred")
      console.log(`Error occurred: ${error}`)
    }
    finally{
      setIsLoading(false)
    }
  }

  const cleanText = (text) => {
    if (!text) return '';
    
    return text.replace(/\s+/g, ' ')
      .replace(/\*\*(.*?)\*\*/g, '$1') 
      .replace(/\*(.*?)\*/g, '$1')       
      .replace(/\*/g, '')        
      .replace(/__(.*?)__/g, '$1') 
      .replace(/`(.*?)`/g, '$1')       
      .replace(/^(Based on the document|According to the text|The document states|In summary)[,:]\s*/i, '')
      .replace(/\s*(Let me know if you need.*|Is there anything else.*|Hope this helps.*)\s*$/i, '')
      .replace(/^\s*[-•*]\s+/gm, '• ') 
      .replace(/^\s*\d+\.\s+/gm, '')
      .replace(/[.]{2,}/g, '.')
      .replace(/[!]{2,}/g, '!')
      .replace(/[?]{2,}/g, '?')
      .replace(/\n\s*\n\s*\n/g, '\n\n') 
      .replace(/^\s+|\s+$/g, '')        
      .replace(/^./, str => str.toUpperCase());
  };

  const handleAsk = async() => {
    if(!pdfData){
      alert("First select and ingest the pdf")
      return
    }
    if(!isIngested){
      alert("Firstly ingest the pdf")
      return
    }
    if(!question){
      alert("Enter the question - it can't be blank")
      return
    }
    setIsLoading(true)
    try {
      const response = await axios.post("http://127.0.0.1:8000/ask", {question: question}, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if(response.data.status == "success"){
        let a = response.data.answer;
        setAns(cleanText(a))
        alert('Your Answer is ready!!')
      }
      else{
        alert("An error occurred: " + response.data.message)
        console.log(response.data.message)
      }
    } catch (error) {
      alert(`An error occurred: ${error}!`)
      console.log("Error that occurred: " + error);
    }
    finally{
      setIsLoading(false)
    }
  }

  const handleUploadNew = () => {
    setPdfData(null);
    setIsIngested(false);
    setIngestedFileName('');
    setAns('');
    setQuestion('');
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-black">
      {isLoading ? (
        <Loading/>
      ) : (
        <div className="p-6 max-w-5xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent mb-2">
              PDF RAG Assistant
            </h1>
            <p className="text-gray-400 text-lg">
              Upload your PDF and ask intelligent questions
            </p>
          </div>
          {!isIngested ? (
            <div className="mb-8 bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 shadow-2xl">
              <div className="mb-4 text-xl font-semibold text-gray-100 flex items-center">
                <span className="mr-3 text-2xl">📁</span>
                Upload your PDF file
              </div>
              
              <input 
                type="file" 
                accept=".pdf"
                onChange={handleChange} 
                name='updf' 
                className="mb-4 block w-full text-sm text-gray-300 bg-gray-700/50 border border-gray-600 rounded-xl p-3 
                          file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium 
                          file:bg-gradient-to-r file:from-blue-500 file:to-purple-600 file:text-white 
                          hover:file:from-blue-600 hover:file:to-purple-700 file:transition-all file:duration-200 
                          file:shadow-lg hover:file:shadow-xl"
              />
              
              {pdfData && (
                <div className="mb-4 text-cyan-400 flex items-center bg-cyan-400/10 p-3 rounded-lg border border-cyan-400/20">
                  <span className="mr-2 text-lg">📄</span>
                  <span className="font-medium">Selected: {pdfData.name}</span>
                </div>
              )}
              
              <button 
                onClick={handleIngest}
                disabled={!pdfData}
                className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 ${
                  pdfData 
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white' 
                    : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                }`}
              >
                <span className="flex items-center">
                  <span className="mr-2">⚡</span>
                  Ingest PDF
                </span>
              </button>
            </div>
          ) : (
            <div className="mb-8 p-6 bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/30 rounded-2xl backdrop-blur-sm shadow-2xl">
              <div className="text-emerald-400 font-bold text-lg flex items-center mb-2">
                <span className="mr-3 text-xl">✅</span>
                PDF Successfully Ingested
              </div>
              <div className="text-emerald-300 flex items-center mb-4">
                <span className="mr-2 text-lg">📄</span>
                <span className="font-medium">{ingestedFileName}</span>
              </div>
              <button 
                onClick={handleUploadNew}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 hover:text-white text-sm rounded-lg transition-all duration-200 border border-gray-600 hover:border-gray-500"
              >
                🔄 Upload New File
              </button>
            </div>
          )}
          <div className="mb-8 bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 shadow-2xl">
            <div className="mb-4 text-xl font-semibold text-gray-100 flex items-center">
              <span className="mr-3 text-2xl">💬</span>
              Ask a Question
            </div>
            
            <input 
              type="text" 
              placeholder='What would you like to know about this PDF?' 
              onChange={handleChange} 
              name='ques' 
              value={question}
              disabled={!isIngested}
              className={`w-full p-4 mb-4 border rounded-xl transition-all duration-200 text-lg font-medium ${
                !isIngested 
                  ? 'bg-gray-700/30 border-gray-600 text-gray-500 placeholder-gray-600' 
                  : 'bg-gray-700/50 border-gray-600 text-gray-100 placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/50'
              } focus:outline-none`}
            />
            
            <button 
              onClick={handleAsk}
              disabled={!isIngested || !question.trim()}
              className={`px-8 py-3 rounded-xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 ${
                (isIngested && question.trim()) 
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white' 
                  : 'bg-gray-600 text-gray-400 cursor-not-allowed'
              }`}
            >
              <span className="flex items-center">
                <span className="mr-2">🤖</span>
                Ask Question
              </span>
            </button>
          </div>

          {ans && (
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 shadow-2xl">
              <h3 className="text-2xl font-bold text-gray-100 mb-4 flex items-center">
                <span className="mr-3 text-2xl">💡</span>
                Answer
              </h3>
              <div className="bg-gradient-to-br from-gray-700/50 to-gray-800/50 border border-gray-600/50 rounded-xl p-6 min-h-[120px] text-gray-200 leading-relaxed text-lg whitespace-pre-line shadow-inner">
                {ans}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Home