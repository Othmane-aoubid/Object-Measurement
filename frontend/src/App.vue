<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
    <h1 class="text-3xl font-bold mb-6 text-gray-800">Object Measurement</h1>
    
    <div class="w-full max-w-md bg-white rounded-lg shadow-md overflow-hidden">
      <div class="p-4">
        <video ref="video" class="w-full h-auto mb-4" autoplay playsinline></video>
        
        <button @click="captureImage" class="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition duration-300 mb-4">
          Capture Image
        </button>
        
        <canvas ref="canvas" class="w-full h-auto mb-4" style="display: none;"></canvas>
        
        <div v-if="measurements" class="bg-gray-100 p-4 rounded">
          <h2 class="text-xl font-semibold mb-2">Measurements:</h2>
          <p>Width: {{ measurements.width }} pixels</p>
          <p>Height: {{ measurements.height }} pixels</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const video = ref(null)
const canvas = ref(null)
const measurements = ref(null)
let stream = null

onMounted(async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
    video.value.srcObject = stream
  } catch (error) {
    console.error('Error accessing camera:', error)
  }
})

onUnmounted(() => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
  }
})

const captureImage = () => {
  const context = canvas.value.getContext('2d')
  canvas.value.width = video.value.videoWidth
  canvas.value.height = video.value.videoHeight
  context.drawImage(video.value, 0, 0, canvas.value.width, canvas.value.height)
  
  const imageData = canvas.value.toDataURL('image/jpeg')
  sendImageToBackend(imageData)
}

const sendImageToBackend = async (imageData) => {
  try {
    const response = await fetch('http://localhost:5000/measure', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image: imageData }),
    })
    const data = await response.json()
    measurements.value = data
  } catch (error) {
    console.error('Error sending image to backend:', error)
  }
}
</script>