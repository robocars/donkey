import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

import Tubes from './components/tubes';

class App extends Component {
  render() {
    return (
      <div className="App">
        <div className="container">
          <div className="row">
            <div className="col-md-6">
              <div className="row">
                <Tubes/>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default App;
