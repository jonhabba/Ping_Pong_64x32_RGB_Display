const express = require('express')
const app = express()
var cors = require('cors')
app.use(cors())
app.use(express.json());

const data = {
  "leftup": false,
  "leftdown": false,
  "rightup": false,
  "rightdown": false
}

app.get('/', (req, res) => {
  res.send(data)
})



    app.post('/left', (req, res) => {
        try {
            const { up, down } = req.body
            if (up === undefined || down === undefined) {
                return res.status(400).json({ error: 'Missing up or down values' })
            }
            data.leftup = up
            data.leftdown = down
            res.json({ recieved_up: up, received_down: down })
        } catch (error) {
            res.status(500).json({ error: error.message })
        }
    })

    app.post('/right', (req, res) => {
      try {
          const { up, down } = req.body
          if (up === undefined || down === undefined) {
              return res.status(400).json({ error: 'Missing up or down values' })
          }
          data.rightup = up
          data.rightdown = down
          res.json({ recieved_up: up, received_down: down })
      } catch (error) {
          res.status(500).json({ error: error.message })
      }
  })
    

app.listen(3000, "0.0.0.0")