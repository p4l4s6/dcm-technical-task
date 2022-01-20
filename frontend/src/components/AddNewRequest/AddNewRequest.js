import React, {Component, useRef} from 'react';
import axios from "../../axios-api";

class AddNewRequest extends Component {
    constructor(props) {
        super(props)
        this.state = {
            selectedFile: null
        }
    }

    onChangeHandler = event => {
        const selectedFile = event.target.files[0]
        const formData = new FormData();
        formData.append(
            "test_file",
            selectedFile,
        );
        axios.post('upload', formData).then(response => {
            console.log("Upload complete");
            this.props.refeshTest();
        }).catch(error => {
            console.log(error)
        })


    }
    onButtonClick = () => {
        this.upload.click()
    };

    render() {

        return (
            <div className="row">
                <div className="col-md-12">
                    <input type='file' ref={(ref) => {
                        return this.upload = ref;
                    }} id='file' style={{display: 'none'}} onChange={this.onChangeHandler}/>
                    <button onClick={this.onButtonClick} className="btn btn-info float-right">Upload New Test</button>
                </div>
                <div className="col-md-12">
                    <fieldset>
                        <legend>New request</legend>
                        <form>
                            <div className="row">
                                <div className="col-md-3 form-group">
                                    <input type="text" className="form-control" name="requester" id="requester"
                                           placeholder="Requester" value={this.props.requester}
                                           onChange={this.props.requesterChanged.bind(this)}/>
                                    <p className="error-message">{this.props.requesterError}</p>
                                </div>
                                <div className="col-md-3 form-group">
                                    <select className="form-control" name="env_id" id="env_id"
                                            placeholder="Environment ID"
                                            value={this.props.env} onChange={this.props.envChanged.bind(this)}>
                                        <option value="" defaultValue></option>
                                        {this.props.assets.test_envs.map(item => <option value={item.id}
                                                                                         key={item.id}>{item.name}</option>)}
                                    </select>
                                    <p className="error-message">{this.props.envError}</p>
                                </div>
                                <div className="col-md-4 form-group">
                                    <select className="form-control" name="test_path" id="test_path" multiple
                                            placeholder="Test Path" value={this.props.testPath}
                                            onChange={this.props.testPathChanged.bind(this)}>
                                        <option value="" defaultValue></option>
                                        {this.props.assets.available_paths.map(item => <option value={item.id}
                                                                                               key={item.id}>{item.path}</option>)}
                                    </select>
                                    <p className="error-message">{this.props.testPathError}</p>
                                </div>
                                <div className="col-md-2">
                                    <input type="button" className="btn btn-primary" value="Submit"
                                           disabled={this.props.testPath === '' || this.props.requester === '' || this.props.env === ''}
                                           onClick={this.props.submitTest}/>
                                </div>
                            </div>
                        </form>
                    </fieldset>
                </div>
            </div>
        );
    }
}

export default AddNewRequest;