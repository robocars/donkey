import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

import Tubes from './components/tubes';
import Models from './components/models';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
        tempBaseUrl: ''
    }
  }
  onApiBaseUrlChange() {
    const self = this;
    return (e) => {
      self.setState({
        tempBaseUrl: e.target.value
      })
    }
  }
  validateApiUrl() {
    const self = this;
    return (e) => {
      self.setState({
        apiBaseUrl: self.state.tempBaseUrl
      })
    }
  }
  render() {
    return (
      <div className="App">
        <div className="container">
          <div className="row">
            <label>API base url :</label><input type="text" onChange={this.onApiBaseUrlChange()} value={this.state.tempBaseUrl} onBlur={this.validateApiUrl()} />
          </div>
          <div className="row">
            <div className="col-md-6">
              <Tubes apiBaseUrl={this.state.apiBaseUrl} />
            </div>
            <div className="col-md-6">
              <Models apiBaseUrl={this.state.apiBaseUrl} />
            </div>
      </div>
        </div>
      </div>
    );
  }
}

export default App;
