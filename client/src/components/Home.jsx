import React, { useState } from 'react'
import axios from "axios"
import Loading from './Loading';

const Home = () => {
  const [selectedFiles, setSelectedFiles] = useState([]); // ✅ For multiple files
  const [question, setQuestion] = useState('');
  const [isIngested, setIsIngested] = useState(false);
  const [isLoading, setIsLoading] = useState(false)
  const [ans, setAns] = useState('');
  const [sources, setSources] = useState({}); // ✅ For source tracking
  const [ingestedFileNames, setIngestedFileNames] = useState([]); // ✅ Multiple filenames

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    
    if (name === 'updf') {
      const fileList = Array.from(files); // ✅ Convert FileList to Array
      setSelectedFiles(fileList);
      setIsIngested(false);
      setIngestedFileNames([]);
      setAns('');
      setSources({});
    } else if (name === 'ques') {
      setQuestion(value);
    }
  }

  const handleIngest = async() => {
    if(!selectedFiles || selectedFiles.length === 0){
      alert("Upload at least one PDF file first")
      return
    }
    setIsLoading(true)
    try {
      const formData = new FormData()
      
      // ✅ Append all selected files with 'files' key (matches backend)
      selectedFiles.forEach(file => {
        formData.append('files', file);
      });
      
      const response = await axios.post("http://127.0.0.1:8000/ingest", formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      if(response.data.status == "success"){
        alert(`${response.data.data.count} file(s) ingested successfully`)
        setIsIngested(true)
        setIngestedFileNames(response.data.data.filenames); // ✅ Store array of filenames
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
    if(!selectedFiles || selectedFiles.length === 0){
      alert("First select and ingest PDF files")
      return
    }
    if(!isIngested){
      alert("Firstly ingest the PDF files")
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
        setSources(response.data.sources || {}); // ✅ Store source information
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
    setSelectedFiles([]);
    setIsIngested(false);
    setIngestedFileNames([]);
    setAns('');
    setSources({});
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
              Upload your PDFs and ask intelligent questions
            </p>
          </div>
          
          {/* ✅ File Upload Section - Updated for multiple files */}
          {!isIngested ? (
            <div className="mb-8 bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 shadow-2xl">
              <div className="mb-4 text-xl font-semibold text-gray-100 flex items-center">
                <span className="mr-3 text-2xl">📁</span>
                Upload your PDF files
              </div>
              
              <input 
                type="file" 
                accept=".pdf"
                onChange={handleChange} 
                name='updf' 
                multiple // ✅ Allow multiple file selection
                className="mb-4 block w-full text-sm text-gray-300 bg-gray-700/50 border border-gray-600 rounded-xl p-3 
                          file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium 
                          file:bg-gradient-to-r file:from-blue-500 file:to-purple-600 file:text-white 
                          hover:file:from-blue-600 hover:file:to-purple-700 file:transition-all file:duration-200 
                          file:shadow-lg hover:file:shadow-xl"
              />
              
              {/* ✅ Display selected files */}
              {selectedFiles.length > 0 && (
                <div className="mb-4 text-cyan-400 bg-cyan-400/10 p-3 rounded-lg border border-cyan-400/20">
                  <span className="mr-2 text-lg">📄</span>
                  <span className="font-medium">
                    Selected: {selectedFiles.length} file(s)
                  </span>
                  <div className="mt-2 text-sm text-cyan-300 max-h-32 overflow-y-auto">
                    {selectedFiles.map((file, index) => (
                      <div key={index} className="flex items-center">
                        <span className="mr-2">•</span>
                        <span>{file.name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              <button 
                onClick={handleIngest}
                disabled={selectedFiles.length === 0}
                className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 ${
                  selectedFiles.length > 0
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white' 
                    : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                }`}
              >
                <span className="flex items-center">
                  <span className="mr-2">⚡</span>
                  Ingest {selectedFiles.length > 0 ? `${selectedFiles.length} PDF${selectedFiles.length > 1 ? 's' : ''}` : 'PDFs'}
                </span>
              </button>
            </div>
          ) : (
            /* ✅ Ingested Files Display - Updated for multiple files */
            <div className="mb-8 p-6 bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/30 rounded-2xl backdrop-blur-sm shadow-2xl">
              <div className="text-emerald-400 font-bold text-lg flex items-center mb-2">
                <span className="mr-3 text-xl">✅</span>
                {ingestedFileNames.length} PDF{ingestedFileNames.length > 1 ? 's' : ''} Successfully Ingested
              </div>
              <div className="text-emerald-300 mb-4">
                <div className="flex items-center mb-2">
                  <span className="mr-2 text-lg">📄</span>
                  <span className="font-medium">Files:</span>
                </div>
                <div className="ml-6 max-h-24 overflow-y-auto">
                  {ingestedFileNames.map((filename, index) => (
                    <div key={index} className="text-sm text-emerald-200">
                      • {filename}
                    </div>
                  ))}
                </div>
              </div>
              <button 
                onClick={handleUploadNew}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 hover:text-white text-sm rounded-lg transition-all duration-200 border border-gray-600 hover:border-gray-500"
              >
                🔄 Upload New Files
              </button>
            </div>
          )}

          {/* Question Section */}
          <div className="mb-8 bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 shadow-2xl">
            <div className="mb-4 text-xl font-semibold text-gray-100 flex items-center">
              <span className="mr-3 text-2xl">💬</span>
              Ask a Question
            </div>
            
            <input 
              type="text" 
              placeholder='What would you like to know about these PDFs?' 
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

          {/* ✅ Answer Section with Source Attribution */}
          {ans && (
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 shadow-2xl">
              <h3 className="text-2xl font-bold text-gray-100 mb-4 flex items-center">
                <span className="mr-3 text-2xl">💡</span>
                Answer
              </h3>
              <div className="bg-gradient-to-br from-gray-700/50 to-gray-800/50 border border-gray-600/50 rounded-xl p-6 min-h-[120px] text-gray-200 leading-relaxed text-lg whitespace-pre-line shadow-inner">
                {ans}
              </div>
              
              {/* ✅ Sources Section */}
              {sources.source_details && sources.source_details.length > 0 && (
                <div className="mt-6 bg-blue-900/20 border border-blue-700/30 rounded-xl p-4">
                  <h4 className="text-lg font-semibold text-blue-300 mb-3 flex items-center">
                    <span className="mr-2">📚</span>
                    Sources ({sources.total_chunks_used} chunks analyzed)
                  </h4>
                  
                  {/* Source Details */}
                  <div className="space-y-2 mb-4">
                    {sources.pages_referenced && sources.pages_referenced.map((pageRef, index) => (
                      <div key={index} className="flex items-center justify-between text-blue-200 text-sm bg-blue-900/10 p-2 rounded">
                        <div className="flex items-center">
                          <span className="mr-2">📄</span>
                          <span>{pageRef}</span>
                        </div>
                        {sources.source_details[index] && (
                          <span className="text-blue-400 text-xs bg-blue-800/30 px-2 py-1 rounded">
                            {sources.source_details[index].relevance}% relevant
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                  
                  {/* Files Summary */}
                  {sources.files_referenced && sources.files_referenced.length > 0 && (
                    <div className="border-t border-blue-700/30 pt-3">
                      <div className="text-xs text-blue-400 mb-1">Files Referenced:</div>
                      <div className="flex flex-wrap gap-2">
                        {sources.files_referenced.map((file, index) => (
                          <span key={index} className="bg-blue-800/30 text-blue-200 text-xs px-2 py-1 rounded">
                            {file}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Home