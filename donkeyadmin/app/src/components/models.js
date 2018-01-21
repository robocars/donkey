import React, { Component } from 'react';
import { getModels } from '../api/models.api';
import config from '../config';

class Models extends Component {
    constructor(props) {
        super(props);
        this.state = {
            models: [],
            apiBaseUrl: ''
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
    render() {
        return (
            <div>
                <h1>Models</h1>
                <form action={`${this.state.apiBaseUrl}/models`} method="post" enctype="multipart/form-data">
                <input type="file" name="model" /><input type="submit"/>
                </form>
                <ul className="list-group">
                {(this.state.models || []).map((model) => {
                    return <li className="list-group-item"><a href={`${this.state.apiBaseUrl}${model.url}`}>{model.name}</a></li>
                })}
                </ul>
            </div>
        )
    }
}

export default Models;