import React, { Component } from 'react';
import { getModels } from '../api/models.api';
import config from '../config';

class Models extends Component {
    constructor(props) {
        super(props);
        this.state = {
            models: [],
            apiBaseUrl: '',
            filename: 'Choose file'
        }
    }
    async loadModels(baseUrl) {
        const models = await getModels(baseUrl);
        this.setState({
            models,
            apiBaseUrl: baseUrl
        });
    }
    async componentWillMount() {
        await this.loadModels(this.props.apiBaseUrl);
    }
    async componentWillReceiveProps(nextProps) {
        await this.loadModels(nextProps.apiBaseUrl);
    }
    onFileChange() {
        const self = this;
        return (e) => {
            self.setState({
                filename: e.target.value
            })
        }
    }
    render() {
        return (
            <div>
                <h1>Models</h1>
                <form action={`${this.state.apiBaseUrl}/models`} method="post" encType="multipart/form-data" target="_blank">
                    <div className="input-group mb-3">
                        <div className="custom-file">
                            <input type="file" className="custom-file-input" id="inputGroupFile02" name="model" onChange={this.onFileChange()}/>
                            <label className="custom-file-label">{this.state.filename}</label>
                        </div>
                        <div className="input-group-append">
                        <input type="submit" value="Upload" className="input-group-text"/>
                        </div>
                    </div>                   
                    
                </form>
                <ul className="list-group">
                {(this.state.models || []).map((model, idx) => {
                    return <li className="list-group-item" key={idx}>
                    <div className="row">
                        <div className="col-md-10"><span>{model.name}</span></div>
                        <div className="col-md-2"><button type="button" class="btn btn-outline-primary">Drive</button></div>
                    </div>
                    </li>
                })}
                </ul>
            </div>
        )
    }
}

export default Models;