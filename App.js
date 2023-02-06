import React, {useRef, useEffect, useState} from "react";
import image003 from "./image003.png";

const AudioRecorder = () => { 

  const [audioBlob, setAudioBlob] = useState(null);
  const [result, setResult] = useState("");

  const [data, setdata] = useState({
    word_1: "",
    word_2: "",
    word_3: "",
    word_4: "",
  });

  // Using useEffect for single rendering
  useEffect(() => {
    // Using fetch to fetch the api from 
    // flask server it will be redirected to proxy
    fetch("/data").then((res) =>
        res.json().then((data) => {
            // Setting a data from api
            //console.log(data.word_1);
            setdata({
                word_1: data.word_1,
                word_2: data.word_2,
                word_3: data.word_3,
                word_4: data.word_4,
            });
        })
    );
  }, []);

  const videoRef = useRef(null);

  const getVideo = () => {
    navigator.mediaDevices
    .getUserMedia({
      video : {width: 1920, height: 1080}
    })
    .then(stream => {
      let video = videoRef.current;
      video.srcObject = stream;
      video.play();
    })
    .catch(err => {
      console.err(err);
    })
  }

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    let audioChunks = [];

    mediaRecorder.addEventListener('dataavailable', event => {
      audioChunks.push(event.data);
    });

    mediaRecorder.addEventListener('stop', () => {
      const audioBlob = new Blob(audioChunks);
      setAudioBlob(audioBlob);
    });

    mediaRecorder.start();

    // stop recording after 15 seconds
    setTimeout(() => {
      mediaRecorder.stop();
      stream.getTracks().forEach(track => track.stop());
    }, 15000);
  };

  /*function show()
  {
    //console.log(audioBlob);
    console.log(typeof audioBlob);
  }*/

  const downloadRecording = () => {
    //const pathName = `download`;
    try {
        // for Chrome
        const link = document.createElement("a");
        link.href = URL.createObjectURL(audioBlob);
        link.download = "recorded-audio.wav";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (err) {
      console.error(err);
    }
  };

  const uploadAudio = async () => {
    try {
      const response = await fetch('http://localhost:3000/upload', {
        method: 'POST',
        body: audioBlob,
        headers: {
          'Content-Type': 'audio/mp3',
        },
      });
      const data = await response.json();
      console.log(data);
    } catch (error) {
      console.log(error);
    }
  };

  const assess = async () => {
    const response = await fetch("http://localhost:3000/assess");
    const data = await response.text();
    setResult(data);
  };

  useEffect(() => {
    getVideo();
  }, [videoRef])

  return (
    <div>

      <div className="container_head">
        <h1 className="main_head"><img src={image003} alt="react logo" height = "70"/></h1>
      </div>

      <div className="container_screen">
          <p className="wordone">{data.word_1}</p>
          <p className="wordtwo">{data.word_2}</p>
          <p className="wordthree">{data.word_3}</p>
          <p className="wordfour">{data.word_4}</p>
          <video ref={videoRef}></video>
      </div> 

      <div className="buttons">
        <button className = "btn_start" onClick={startRecording}>Start Recording</button>
        {audioBlob && <audio src={URL.createObjectURL(audioBlob)} controls />}         
        <button className = "btn_upload" onClick={uploadAudio}>Upload Audio</button>
        <button className = "btn_dwnld" onClick={downloadRecording}>download</button>
        <button onClick={assess}>Run Python Script</button>
        <p>{result}</p>
      </div>

    </div>
  );
}

export default AudioRecorder;
