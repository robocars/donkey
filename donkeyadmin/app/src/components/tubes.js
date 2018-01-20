import React, { Component } from 'react';
import { getTubes } from '../api/tubes.api';
import config from '../config';

class Tubes extends Component {
    constructor(props) {
        super(props);
        this.state = {
            tubes: []
        }
    }
    async componentWillMount() {
        const tubes = await getTubes();
        this.setState({
            tubes
        });
    }
    render() {
        return (
            <div>
            <h1>Tubes</h1>
            <ul className="list-group">
            {(this.state.tubes || []).map((tub) => {
                return <li className="list-group-item"><a href={`${config.apiBaseUrl}${tub.url}`}>{tub.name}</a></li>
            })}
            </ul>
            </div>
        )
    }
}

export default Tubes;