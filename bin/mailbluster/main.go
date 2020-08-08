package main

import (
	"bytes"
	"crypto/md5"
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"os"
)

type lead struct {
	email string
}

func (l *lead) hash() string {
	hash := md5.Sum([]byte(l.email))
	return fmt.Sprintf("%x", hash)
}

func (l *lead) unsubscribe(client *api) error {
	endpoint := fmt.Sprintf("/leads/%s", l.hash())
	body := struct {
		Subscribed bool `json:"subscribed"`
	}{}
	result := struct {
		Message string `json:"message"`
	}{}
	err := client.put(endpoint, body, &result)
	if err != nil {
		if result.Message == "" {
			return err
		}
		return fmt.Errorf("%s: %w", result.Message, err)
	}
	return nil
}

type api struct {
	key         string
	base        string
	contentType string
}

func (client *api) put(endpoint string, input, output interface{}) error {
	var payload *bytes.Buffer
	if input != nil {
		data, err := json.Marshal(input)
		if err != nil {
			return err
		}
		payload = bytes.NewBuffer(data)
	}
	uri, err := url.Parse(client.base)
	if err != nil {
		return err
	}
	uri.Path += endpoint
	req, err := http.NewRequest(http.MethodPut, uri.String(), payload)
	if err != nil {
		return err
	}
	req.Header.Add("Authorization", client.key)
	req.Header.Set("Content-Type", client.contentType)
	res, err := http.DefaultClient.Do(req)
	if err != nil {
		return err
	}
	defer res.Body.Close()
	data, err := ioutil.ReadAll(res.Body)
	if err != nil {
		return err
	}
	if err = json.Unmarshal(data, output); err != nil {
		return err
	}
	if res.StatusCode != http.StatusOK {
		return errors.New(res.Status)
	}
	return nil
}

const (
	endpoint    = "https://api.mailbluster.com/api"
	contentType = "application/json"
)

func main() {
	args := os.Args[1:]
	if len(args) != 2 {
		fmt.Fprintln(os.Stderr, "usage: mailbluster apikey lead")
		os.Exit(1)
	}
	client := &api{
		key:         args[0],
		base:        endpoint,
		contentType: contentType,
	}
	contact := &lead{
		email: args[1],
	}
	if err := contact.unsubscribe(client); err != nil {
		err = fmt.Errorf("%s: %w", contact.email, err)
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	fmt.Fprintf(os.Stdout, "%s: OK\n", contact.email)
}
