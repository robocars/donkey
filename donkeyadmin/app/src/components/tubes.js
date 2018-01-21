import React, { Component } from 'react';
import { getTubes } from '../api/tubes.api';
import config from '../config';

class Tubes extends Component {
    constructor(props) {
        super(props);
        this.state = {
            tubes: [],
            apiBaseUrl: ''
        }
    }
    async loadTubes(baseUrl) {
        const tubes = await getTubes(baseUrl);
        this.setState({
            tubes,
            apiBaseUrl: baseUrl
        });
    }
    async componentWillMount() {
        await this.loadTubes(this.props.apiBaseUrl);
    }
    async componentWillReceiveProps(nextProps) {
        await this.loadTubes(nextProps.apiBaseUrl);
    }
    render() {
        return (
            <div>
            <h1>Tubes</h1>
            <ul className="list-group">
            {(this.state.tubes || []).map((tub) => {
                return <li className="list-group-item"><a href={`${this.state.apiBaseUrl}${tub.url}`}>{tub.name}</a></li>
            })}
            </ul>
            </div>
        )
    }
}

export default Tubes;